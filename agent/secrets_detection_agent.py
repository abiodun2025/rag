#!/usr/bin/env python3
"""
Secrets Detection Agent
Handles scanning files and directories for secrets and vulnerabilities.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SecretsDetectionAgent:
    """Agent for detecting secrets and vulnerabilities in files and directories."""
    
    def __init__(self, mcp_server_url: str = None):
        """Initialize the secrets detection agent."""
        self.mcp_server_url = mcp_server_url
        self.secret_patterns = [
            # API Keys
            r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{32,}["\']?',
            r'api[_-]?token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{32,}["\']?',
            
            # AWS Keys
            r'AKIA[0-9A-Z]{16}',
            r'aws[_-]?access[_-]?key[_-]?id["\']?\s*[:=]\s*["\']?AKIA[0-9A-Z]{16}["\']?',
            r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9/+=]{40}["\']?',
            
            # Database Credentials
            r'password["\']?\s*[:=]\s*["\']?[^\s"\']{8,}["\']?',
            r'db[_-]?password["\']?\s*[:=]\s*["\']?[^\s"\']{8,}["\']?',
            r'connection[_-]?string["\']?\s*[:=]\s*["\']?[^\s"\']{20,}["\']?',
            
            # Private Keys
            r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
            r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
            
            # OAuth Tokens
            r'oauth[_-]?token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{32,}["\']?',
            r'bearer[_-]?token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{32,}["\']?',
            
            # Generic Secrets
            r'secret["\']?\s*[:=]\s*["\']?[^\s"\']{8,}["\']?',
            r'key["\']?\s*[:=]\s*["\']?[^\s"\']{16,}["\']?',
        ]
        
        self.risk_levels = {
            'critical': ['AKIA[0-9A-Z]{16}', '-----BEGIN.*PRIVATE KEY-----'],
            'high': ['api[_-]?key', 'password', 'secret'],
            'medium': ['token', 'key'],
            'low': ['connection[_-]?string']
        }
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scan a single file for secrets."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "secrets_found": 0
                }
            
            # Skip binary files and common non-text files
            if self._is_binary_file(file_path):
                return {
                    "success": True,
                    "file_path": str(file_path),
                    "secrets_found": 0,
                    "note": "Binary file - skipped for security scanning"
                }
            
            secrets_found = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in self.secret_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            secret_info = {
                                "line": i,
                                "pattern": pattern,
                                "match": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                                "risk_level": self._assess_risk_level(pattern)
                            }
                            secrets_found.append(secret_info)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "secrets_found": len(secrets_found),
                "secrets": secrets_found,
                "risk_level": self._calculate_overall_risk(secrets_found)
            }
            
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": str(file_path)
            }
    
    def scan_directory(self, dir_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Scan a directory for secrets."""
        try:
            dir_path = Path(dir_path)
            if not dir_path.exists() or not dir_path.is_dir():
                return {
                    "success": False,
                    "error": f"Directory not found: {dir_path}",
                    "files_scanned": 0
                }
            
            files_to_scan = []
            if recursive:
                files_to_scan = list(dir_path.rglob('*'))
            else:
                files_to_scan = list(dir_path.iterdir())
            
            # Filter for text files only
            text_files = [f for f in files_to_scan if f.is_file() and not self._is_binary_file(f)]
            print(f"🔍 Found {len(text_files)} text files to scan")
            
            # Limit the number of files to scan to avoid timeouts
            max_files = 100
            if len(text_files) > max_files:
                print(f"🔍 Limiting scan to first {max_files} files to avoid timeout")
                text_files = text_files[:max_files]
            
            total_secrets = 0
            files_with_secrets = 0
            scan_results = []
            
            for i, file_path in enumerate(text_files):
                print(f"🔍 Scanning file {i+1}/{len(text_files)}: {file_path.name}")
                result = self.scan_file(str(file_path))
                if result["success"] and result["secrets_found"] > 0:
                    files_with_secrets += 1
                    total_secrets += result["secrets_found"]
                scan_results.append(result)
            
            overall_risk = self._calculate_overall_risk_from_results(scan_results)
            
            result = {
                "success": True,
                "directory": str(dir_path),
                "files_scanned": len(text_files),
                "files_with_secrets": files_with_secrets,
                "total_secrets": total_secrets,
                "scan_results": scan_results,
                "risk_level": overall_risk
            }
            
            print(f"🔍 Directory scan completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error scanning directory {dir_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "directory": str(dir_path)
            }
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True
    
    def _assess_risk_level(self, pattern: str) -> str:
        """Assess the risk level of a detected pattern."""
        for level, patterns in self.risk_levels.items():
            for p in patterns:
                if re.search(p, pattern, re.IGNORECASE):
                    return level
        return 'low'
    
    def _calculate_overall_risk(self, secrets: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level from detected secrets."""
        if not secrets:
            return 'LOW'
        
        risk_scores = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        max_risk = max(risk_scores.get(secret['risk_level'], 1) for secret in secrets)
        
        if max_risk >= 4:
            return 'CRITICAL'
        elif max_risk >= 3:
            return 'HIGH'
        elif max_risk >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_overall_risk_from_results(self, results: List[Dict[str, Any]]) -> str:
        """Calculate overall risk from multiple scan results."""
        all_secrets = []
        for result in results:
            if result.get("success") and result.get("secrets"):
                all_secrets.extend(result["secrets"])
        
        return self._calculate_overall_risk(all_secrets)
    
    def generate_report(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        if not scan_results.get("success"):
            return {
                "success": False,
                "error": scan_results.get("error", "Scan failed")
            }
        
        timestamp = datetime.now().isoformat()
        
        if "file_path" in scan_results:
            # Single file scan
            return {
                "success": True,
                "report": {
                    "scan_type": "file_scan",
                    "target": scan_results["file_path"],
                    "timestamp": timestamp,
                    "summary": {
                        "secrets_found": scan_results["secrets_found"],
                        "risk_level": scan_results["risk_level"]
                    },
                    "details": scan_results.get("secrets", [])
                }
            }
        else:
            # Directory scan
            return {
                "success": True,
                "report": {
                    "scan_type": "directory_scan",
                    "target": scan_results["directory"],
                    "timestamp": timestamp,
                    "summary": {
                        "files_scanned": scan_results["files_scanned"],
                        "files_with_secrets": scan_results["files_with_secrets"],
                        "total_secrets": scan_results["total_secrets"],
                        "risk_level": scan_results["risk_level"]
                    },
                    "file_results": scan_results["scan_results"]
                }
            }
    
    async def run_comprehensive_scan(self, target: str) -> Dict[str, Any]:
        """Run a comprehensive secrets detection scan."""
        try:
            logger.info(f"🔍 Starting comprehensive scan on target: {target}")
            target_path = Path(target)
            logger.info(f"🔍 Target path: {target_path}, exists: {target_path.exists()}, is_file: {target_path.is_file()}, is_dir: {target_path.is_dir()}")
            
            if target_path.is_file():
                # Single file scan
                logger.info(f"🔍 Performing file scan on: {target_path}")
                scan_result = self.scan_file(str(target_path))
                logger.info(f"🔍 File scan result: {scan_result}")
                report = self.generate_report(scan_result)
                return {
                    "success": True,
                    "action": "secrets_detection_completed",
                    "target": str(target_path),
                    "scan_type": "file",
                    "secrets_count": scan_result.get("secrets_found", 0),
                    "files_scanned": 1,
                    "risk_level": scan_result.get("risk_level", "UNKNOWN"),
                    "results": scan_result,
                    "security_report": report
                }
            elif target_path.is_dir():
                # Directory scan
                logger.info(f"🔍 Performing directory scan on: {target_path}")
                scan_result = self.scan_directory(str(target_path), recursive=True)
                logger.info(f"🔍 Directory scan result: {scan_result}")
                report = self.generate_report(scan_result)
                return {
                    "success": True,
                    "action": "secrets_detection_completed",
                    "target": str(target_path),
                    "scan_type": "directory",
                    "secrets_count": scan_result.get("total_secrets", 0),
                    "files_scanned": scan_result.get("files_scanned", 0),
                    "risk_level": scan_result.get("risk_level", "UNKNOWN"),
                    "results": scan_result,
                    "security_report": report
                }
            else:
                # Default to current directory
                logger.info(f"🔍 Target not found, defaulting to current directory")
                scan_result = self.scan_directory(".", recursive=True)
                logger.info(f"🔍 Current directory scan result: {scan_result}")
                report = self.generate_report(scan_result)
                return {
                    "success": True,
                    "action": "secrets_detection_completed",
                    "target": ".",
                    "scan_type": "comprehensive",
                    "secrets_count": scan_result.get("total_secrets", 0),
                    "files_scanned": scan_result.get("files_scanned", 0),
                    "risk_level": scan_result.get("risk_level", "UNKNOWN"),
                    "results": scan_result,
                    "security_report": report
                }
                
        except Exception as e:
            logger.error(f"Comprehensive scan failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "action": "secrets_detection_error",
                "error": str(e),
                "note": "Secrets detection failed"
            }
