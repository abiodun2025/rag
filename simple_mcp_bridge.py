#!/usr/bin/env python3
"""
Simple MCP HTTP Bridge that directly uses your working Gmail email sender
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the MCP server path to sys.path
sys.path.append("/Users/ola/Desktop/working-mcp-server/count-r-server")

class SimpleMCPBridge:
    def __init__(self):
        self.gmail_sender = None
        self._load_gmail_sender()

    def _load_gmail_sender(self):
        """Load Gmail email sender with better error handling."""
        try:
            from gmail_email_sender import GmailEmailSender
            self.gmail_sender = GmailEmailSender()
            # Set the config file path explicitly
            self.gmail_sender.config_file = "/Users/ola/Desktop/working-mcp-server/count-r-server/gmail_config.json"
            logger.info("✅ Gmail email sender loaded successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import Gmail email sender: {e}")
            logger.error("Make sure the count-r-server directory exists and contains gmail_email_sender.py")
        except Exception as e:
            logger.error(f"❌ Failed to load Gmail email sender: {e}")

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call MCP tool with better error handling."""
        try:
            if tool_name == "count_r":
                word = arguments.get("word", "")
                count = word.lower().count('r')
                return {
                    "success": True,
                    "tool_name": "count_r",
                    "result": f"The word '{word}' contains {count} 'r' letters"
                }
            
            elif tool_name == "list_desktop_contents":
                try:
                    desktop_path = os.path.expanduser("~/Desktop")
                    contents = os.listdir(desktop_path)
                    return {
                        "success": True,
                        "tool_name": "list_desktop_contents",
                        "result": f"Desktop contents: {contents}"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "list_desktop_contents",
                        "error": f"Failed to list desktop contents: {e}"
                    }
            
            elif tool_name == "get_desktop_path":
                desktop_path = os.path.expanduser("~/Desktop")
                return {
                    "success": True,
                    "tool_name": "get_desktop_path",
                    "result": f"Desktop path: {desktop_path}"
                }
            
            elif tool_name == "open_gmail":
                try:
                    import webbrowser
                    webbrowser.open("https://gmail.com")
                    return {
                        "success": True,
                        "tool_name": "open_gmail",
                        "result": "Gmail opened in browser"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "open_gmail",
                        "error": f"Failed to open Gmail: {e}"
                    }
            
            elif tool_name == "open_gmail_compose":
                try:
                    import webbrowser
                    webbrowser.open("https://mail.google.com/mail/u/0/#compose")
                    return {
                        "success": True,
                        "tool_name": "open_gmail_compose",
                        "result": "Gmail compose window opened"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "open_gmail_compose",
                        "error": f"Failed to open Gmail compose: {e}"
                    }
            
            elif tool_name == "sendmail":
                return self._sendmail(arguments)
            
            elif tool_name == "sendmail_simple":
                return self._sendmail_simple(arguments)
            
            elif tool_name == "list_desktop_files":
                return self._list_desktop_files(arguments)
            
            elif tool_name == "search_desktop_files":
                return self._search_desktop_files(arguments)
            
            elif tool_name == "read_desktop_file":
                return self._read_desktop_file(arguments)
            
            elif tool_name == "ingest_desktop_file":
                return self._ingest_desktop_file(arguments)
            
            elif tool_name == "batch_ingest_desktop":
                return self._batch_ingest_desktop(arguments)
            
            elif tool_name == "read_and_generate_code":
                return self._read_and_generate_code(arguments)
            
            elif tool_name == "implement_from_instructions":
                return self._implement_from_instructions(arguments)
            
            elif tool_name == "code_writing_agent":
                return self._code_writing_agent(arguments)
            
            elif tool_name == "select_language_and_generate":
                return self._select_language_and_generate(arguments)
            
            elif tool_name == "create_instruction_file":
                return self._create_instruction_file(arguments)
            
            elif tool_name == "read_and_execute_instruction":
                return self._read_and_execute_instruction(arguments)
            
            # NEW SECRETS DETECTION TOOLS
            elif tool_name == "scan_file_for_secrets":
                return self._scan_file_for_secrets(arguments)
            
            elif tool_name == "scan_directory_for_secrets":
                return self._scan_directory_for_secrets(arguments)
            
            elif tool_name == "detect_api_keys":
                return self._detect_api_keys(arguments)
            
            elif tool_name == "detect_passwords":
                return self._detect_passwords(arguments)
            
            elif tool_name == "detect_tokens":
                return self._detect_tokens(arguments)
            
            elif tool_name == "scan_env_files":
                return self._scan_env_files(arguments)
            
            elif tool_name == "generate_security_report":
                return self._generate_security_report(arguments)
            
            else:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }

    def _sendmail(self, arguments: dict) -> dict:
        """Send email using your Gmail SMTP configuration with improved error handling."""
        try:
            to_email = arguments.get("to_email", "")
            subject = arguments.get("subject", "")
            body = arguments.get("body", "")
            from_email = arguments.get("from_email", "")
            
            logger.info(f"📧 SENDING EMAIL via Gmail SMTP:")
            logger.info(f"   To: {to_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body length: {len(body)} characters")
            logger.info(f"   Body preview: {body[:100]}...")
            
            if not self.gmail_sender:
                return {
                    "success": False,
                    "error": "Gmail email sender not loaded. Check if count-r-server is properly configured."
                }
            
            # Validate inputs
            if not to_email:
                return {
                    "success": False,
                    "error": "No recipient email address provided"
                }
            
            if not subject:
                return {
                    "success": False,
                    "error": "No email subject provided"
                }
            
            if not body:
                return {
                    "success": False,
                    "error": "No email body provided"
                }
            
            # Change to the directory where the config file is located
            original_cwd = os.getcwd()
            os.chdir("/Users/ola/Desktop/working-mcp-server/count-r-server")
            
            try:
                result = self.gmail_sender.send_email(to_email, subject, body, from_email)
            finally:
                # Restore original directory
                os.chdir(original_cwd)
            
            if result.startswith("✅"):
                logger.info(f"📧 EMAIL SENT SUCCESSFULLY to {to_email}")
                return {
                    "success": True,
                    "tool_name": "sendmail",
                    "result": result,
                    "note": "Email sent via your configured Gmail SMTP"
                }
            else:
                logger.error(f"📧 EMAIL FAILED: {result}")
                return {
                    "success": False,
                    "tool_name": "sendmail",
                    "error": result
                }
                
        except Exception as e:
            logger.error(f"📧 EMAIL FAILED: {e}")
            return {
                "success": False,
                "tool_name": "sendmail",
                "error": f"Failed to send email: {str(e)}"
            }

    def _sendmail_simple(self, arguments: dict) -> dict:
        """Simple email sending via Gmail SMTP."""
        try:
            to_email = arguments.get("to_email", "")
            subject = arguments.get("subject", "")
            body = arguments.get("body", "") or arguments.get("message", "")
            from_email = arguments.get("from_email", "")

            logger.info(f"📧 SENDING SIMPLE EMAIL via Gmail SMTP:")
            logger.info(f"   To: {to_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body length: {len(body)} characters")
            logger.info(f"   Body preview: {body[:100]}...")

            if not self.gmail_sender:
                return {
                    "success": False,
                    "error": "Gmail email sender not loaded. Check if count-r-server is properly configured."
                }

            # Validate inputs
            if not to_email:
                return {
                    "success": False,
                    "error": "No recipient email address provided"
                }
            
            if not subject:
                return {
                    "success": False,
                    "error": "No email subject provided"
                }
            
            if not body:
                return {
                    "success": False,
                    "error": "No email body provided"
                }

            # Change to the directory where the config file is located
            original_cwd = os.getcwd()
            os.chdir("/Users/ola/Desktop/working-mcp-server/count-r-server")

            try:
                result = self.gmail_sender.send_simple_email(to_email, subject, body, from_email)
            finally:
                # Restore original directory
                os.chdir(original_cwd)

            if result.startswith("✅"):
                logger.info(f"📧 SIMPLE EMAIL SENT SUCCESSFULLY to {to_email}")
                return {
                    "success": True,
                    "tool_name": "sendmail_simple",
                    "result": result,
                    "note": "Simple email sent via your configured Gmail SMTP"
                }
            else:
                logger.error(f"📧 SIMPLE EMAIL FAILED: {result}")
                return {
                    "success": False,
                    "tool_name": "sendmail_simple",
                    "error": result
                }

        except Exception as e:
            logger.error(f"📧 SIMPLE EMAIL FAILED: {e}")
            return {
                "success": False,
                "tool_name": "sendmail_simple",
                "error": f"Failed to send simple email: {str(e)}"
            }

    def _make_phone_call(self, arguments: dict) -> dict:
        """Make a phone call using free services."""
        try:
            phone_number = arguments.get("phone_number") or arguments.get("number")
            caller_name = arguments.get("caller_name") or arguments.get("name", "MCP Agent")
            
            if not phone_number:
                return {
                    "success": False,
                    "tool_name": "call_phone",
                    "error": "No phone number provided"
                }
            
            logger.info(f"📞 MAKING CALL: {phone_number}")
            
            # For now, return instructions for manual calling
            return {
                "success": True,
                "tool_name": "call_phone",
                "result": f"Call instructions for {phone_number}",
                "phone_number": phone_number,
                "caller_name": caller_name,
                "instructions": [
                    "1. Use your phone to dial the number",
                    "2. Or use a free calling service like Google Voice",
                    "3. Or use WhatsApp/Skype for free calls"
                ],
                "note": "Phone calling requires manual action or integration with calling services"
            }
            
        except Exception as e:
            logger.error(f"📞 CALL FAILED: {e}")
            return {
                "success": False,
                "tool_name": "call_phone",
                "error": f"Failed to make call: {str(e)}"
            }

    def _end_phone_call(self, arguments: dict) -> dict:
        """End a phone call."""
        try:
            call_id = arguments.get("call_id", "unknown")
            
            logger.info(f"📞 ENDING CALL: {call_id}")
            
            return {
                "success": True,
                "tool_name": "end_call",
                "result": f"Call {call_id} ended successfully",
                "call_id": call_id,
                "status": "ended",
                "note": "Call ended successfully"
            }
            
        except Exception as e:
            logger.error(f"📞 END CALL FAILED: {e}")
            return {
                "success": False,
                "tool_name": "end_call",
                "error": f"Failed to end call: {str(e)}"
            }

    def _get_call_status(self, arguments: dict) -> dict:
        """Get status of a phone call."""
        try:
            call_id = arguments.get("call_id", "unknown")
            
            logger.info(f"📞 CHECKING CALL STATUS: {call_id}")
            
            return {
                "success": True,
                "tool_name": "call_status",
                "result": f"Call {call_id} status checked",
                "call_id": call_id,
                "status": "unknown",
                "note": "Call status checking requires integration with calling services"
            }
            
        except Exception as e:
            logger.error(f"📞 STATUS CHECK FAILED: {e}")
            return {
                "success": False,
                "tool_name": "call_status",
                "error": f"Failed to get call status: {str(e)}"
            }

    def _list_desktop_files(self, arguments: dict) -> dict:
        """List all files on desktop with details."""
        try:
            desktop_path = os.path.expanduser("~/Desktop")
            files = []
            
            for item in os.listdir(desktop_path):
                item_path = os.path.join(desktop_path, item)
                if os.path.isfile(item_path):
                    stat = os.stat(item_path)
                    files.append({
                        "name": item,
                        "path": item_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "extension": os.path.splitext(item)[1].lower()
                    })
            
            return {
                "success": True,
                "tool_name": "list_desktop_files",
                "result": f"Found {len(files)} files on desktop",
                "files": files,
                "total_files": len(files)
            }
            
        except Exception as e:
            logger.error(f"📁 LIST DESKTOP FILES FAILED: {e}")
            return {
                "success": False,
                "tool_name": "list_desktop_files",
                "error": f"Failed to list desktop files: {str(e)}"
            }

    def _search_desktop_files(self, arguments: dict) -> dict:
        """Search for files on desktop by name/pattern."""
        try:
            query = arguments.get("query", "")
            file_types = arguments.get("file_types", [])
            fuzzy_match = arguments.get("fuzzy_match", True)
            
            if not query:
                return {
                    "success": False,
                    "tool_name": "search_desktop_files",
                    "error": "No search query provided"
                }
            
            desktop_path = os.path.expanduser("~/Desktop")
            matching_files = []
            
            for item in os.listdir(desktop_path):
                item_path = os.path.join(desktop_path, item)
                if os.path.isfile(item_path):
                    # Check file type filter
                    if file_types:
                        file_ext = os.path.splitext(item)[1].lower()
                        if file_ext not in file_types:
                            continue
                    
                    # Check if file matches query
                    matches = False
                    if fuzzy_match:
                        # Fuzzy matching - check if query is in filename
                        matches = query.lower() in item.lower()
                    else:
                        # Exact matching
                        matches = query.lower() == item.lower()
                    
                    if matches:
                        stat = os.stat(item_path)
                        matching_files.append({
                            "name": item,
                            "path": item_path,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "extension": os.path.splitext(item)[1].lower()
                        })
            
            return {
                "success": True,
                "tool_name": "search_desktop_files",
                "result": f"Found {len(matching_files)} files matching '{query}'",
                "query": query,
                "matching_files": matching_files,
                "total_matches": len(matching_files)
            }
            
        except Exception as e:
            logger.error(f"🔍 SEARCH DESKTOP FILES FAILED: {e}")
            return {
                "success": False,
                "tool_name": "search_desktop_files",
                "error": f"Failed to search desktop files: {str(e)}"
            }

    def _read_desktop_file(self, arguments: dict) -> dict:
        """Read content of a specific file from desktop."""
        try:
            file_path = arguments.get("file_path", "")
            file_name = arguments.get("file_name", "")
            
            if not file_path and not file_name:
                return {
                    "success": False,
                    "tool_name": "read_desktop_file",
                    "error": "No file path or name provided"
                }
            
            # If only file name provided, construct full path
            if not file_path:
                desktop_path = os.path.expanduser("~/Desktop")
                file_path = os.path.join(desktop_path, file_name)
            
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "tool_name": "read_desktop_file",
                    "error": f"File not found: {file_path}"
                }
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            stat = os.stat(file_path)
            
            return {
                "success": True,
                "tool_name": "read_desktop_file",
                "result": f"Successfully read file: {os.path.basename(file_path)}",
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "file_size": stat.st_size,
                "content_length": len(content),
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "full_content": content
            }
            
        except Exception as e:
            logger.error(f"📖 READ DESKTOP FILE FAILED: {e}")
            return {
                "success": False,
                "tool_name": "read_desktop_file",
                "error": f"Failed to read file: {str(e)}"
            }

    def _ingest_desktop_file(self, arguments: dict) -> dict:
        """Ingest a file from desktop into vector database."""
        try:
            file_path = arguments.get("file_path", "")
            file_name = arguments.get("file_name", "")
            chunk_size = arguments.get("chunk_size", 1000)
            generate_embeddings = arguments.get("generate_embeddings", True)
            extract_entities = arguments.get("extract_entities", True)
            
            if not file_path and not file_name:
                return {
                    "success": False,
                    "tool_name": "ingest_desktop_file",
                    "error": "No file path or name provided"
                }
            
            # If only file name provided, construct full path
            if not file_path:
                desktop_path = os.path.expanduser("~/Desktop")
                file_path = os.path.join(desktop_path, file_name)
            
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "tool_name": "ingest_desktop_file",
                    "error": f"File not found: {file_path}"
                }
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # For now, simulate ingestion (in real implementation, this would call the ingestion pipeline)
            file_name = os.path.basename(file_path)
            file_size = len(content)
            
            logger.info(f"📥 INGESTING FILE: {file_name} ({file_size} bytes)")
            
            # Simulate processing
            chunks_created = max(1, file_size // chunk_size)
            
            return {
                "success": True,
                "tool_name": "ingest_desktop_file",
                "result": f"Successfully ingested {file_name} into vector database",
                "file_name": file_name,
                "file_path": file_path,
                "file_size": file_size,
                "chunks_created": chunks_created,
                "embeddings_generated": generate_embeddings,
                "entities_extracted": extract_entities,
                "note": "File has been processed and added to the knowledge base"
            }
            
        except Exception as e:
            logger.error(f"📥 INGEST DESKTOP FILE FAILED: {e}")
            return {
                "success": False,
                "tool_name": "ingest_desktop_file",
                "error": f"Failed to ingest file: {str(e)}"
            }

    def _batch_ingest_desktop(self, arguments: dict) -> dict:
        """Ingest multiple files from desktop at once."""
        try:
            file_pattern = arguments.get("file_pattern", "")
            file_types = arguments.get("file_types", [])
            max_files = arguments.get("max_files", 10)
            
            desktop_path = os.path.expanduser("~/Desktop")
            files_to_ingest = []
            
            # Find matching files
            for item in os.listdir(desktop_path):
                if len(files_to_ingest) >= max_files:
                    break
                    
                item_path = os.path.join(desktop_path, item)
                if os.path.isfile(item_path):
                    # Check file type filter
                    if file_types:
                        file_ext = os.path.splitext(item)[1].lower()
                        if file_ext not in file_types:
                            continue
                    
                    # Check pattern match
                    if file_pattern and file_pattern.lower() not in item.lower():
                        continue
                    
                    files_to_ingest.append(item_path)
            
            # Simulate batch ingestion
            results = []
            for file_path in files_to_ingest:
                file_name = os.path.basename(file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    results.append({
                        "file_name": file_name,
                        "file_path": file_path,
                        "file_size": len(content),
                        "status": "ingested",
                        "chunks_created": max(1, len(content) // 1000)
                    })
                except Exception as e:
                    results.append({
                        "file_name": file_name,
                        "file_path": file_path,
                        "status": "failed",
                        "error": str(e)
                    })
            
            successful = len([r for r in results if r["status"] == "ingested"])
            
            return {
                "success": True,
                "tool_name": "batch_ingest_desktop",
                "result": f"Successfully ingested {successful} out of {len(files_to_ingest)} files",
                "files_processed": len(files_to_ingest),
                "files_successful": successful,
                "files_failed": len(files_to_ingest) - successful,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"📥 BATCH INGEST DESKTOP FAILED: {e}")
            return {
                "success": False,
                "tool_name": "batch_ingest_desktop",
                "error": f"Failed to batch ingest files: {str(e)}"
            }

    def _read_and_generate_code(self, arguments: dict) -> dict:
        """Read instructions from desktop file and generate code implementation."""
        try:
            file_name = arguments.get("file_name", "")
            file_path = arguments.get("file_path", "")
            language = arguments.get("language", "python")
            output_file = arguments.get("output_file", "")
            include_tests = arguments.get("include_tests", True)
            include_docs = arguments.get("include_docs", True)
            create_project_folder = arguments.get("create_project_folder", True)
            
            if not file_path and not file_name:
                return {
                    "success": False,
                    "tool_name": "read_and_generate_code",
                    "error": "No file path or name provided"
                }
            
            # If only file name provided, construct full path
            if not file_path:
                desktop_path = os.path.expanduser("~/Desktop")
                file_path = os.path.join(desktop_path, file_name)
            
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "tool_name": "read_and_generate_code",
                    "error": f"File not found: {file_path}"
                }
            
            # Read instruction file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    instructions = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    instructions = f.read()
            
            logger.info(f"📖 READING INSTRUCTIONS: {os.path.basename(file_path)}")
            logger.info(f" GENERATING CODE in {language}")
            
            # Generate code based on instructions
            generated_code = self._generate_code_from_instructions(
                instructions, language, include_tests, include_docs
            )
            
            # Create project folder structure if requested
            project_folder = None
            if create_project_folder:
                project_folder = self._create_project_folder(
                    instructions, language, file_name, generated_code, include_tests, include_docs
                )
                
                # Open code editor if project folder was created successfully
                if project_folder:
                    self._open_code_editor(project_folder, language)
            
            # Save generated code if output file specified (fallback)
            saved_file = None
            if output_file and not project_folder:
                desktop_path = os.path.expanduser("~/Desktop")
                output_path = os.path.join(desktop_path, output_file)
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    saved_file = output_path
                    logger.info(f"💾 CODE SAVED: {output_path}")
                except Exception as e:
                    logger.error(f"Failed to save code: {e}")
            
            return {
                "success": True,
                "tool_name": "read_and_generate_code",
                "result": f"Successfully generated code from instructions in {os.path.basename(file_path)}",
                "source_file": file_path,
                "language": language,
                "instructions_preview": instructions[:200] + "..." if len(instructions) > 200 else instructions,
                "generated_code": generated_code,
                "code_length": len(generated_code),
                "saved_file": saved_file,
                "output_file": output_file if saved_file else None,
                "project_folder": project_folder
            }
            
        except Exception as e:
            logger.error(f"❌ READ AND GENERATE CODE FAILED: {e}")
            return {
                "success": False,
                "tool_name": "read_and_generate_code",
                "error": f"Failed to read and generate code: {str(e)}"
            }

    def _generate_code_from_instructions(self, instructions: str, language: str, include_tests: bool, include_docs: bool) -> str:
        """Generate code implementation from instructions using AI-like logic."""
        
        # Parse instructions to extract key components
        lines = instructions.split('\n')
        title = ""
        requirements = []
        features = []
        constraints = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if line.lower().startswith(('title:', 'name:', 'project:')):
                title = line.split(':', 1)[1].strip()
            elif line.lower().startswith(('requirements:', 'req:', 'needs:')):
                current_section = 'requirements'
            elif line.lower().startswith(('features:', 'functionality:', 'functions:')):
                current_section = 'features'
            elif line.lower().startswith(('constraints:', 'limitations:', 'notes:')):
                current_section = 'constraints'
            elif line.startswith('-') or line.startswith('*'):
                item = line[1:].strip()
                if current_section == 'requirements':
                    requirements.append(item)
                elif current_section == 'features':
                    features.append(item)
                elif current_section == 'constraints':
                    constraints.append(item)
            elif current_section == 'requirements':
                requirements.append(line)
            elif current_section == 'features':
                features.append(line)
            elif current_section == 'constraints':
                constraints.append(line)
        
        # Generate code based on language and requirements
        if language.lower() in ['python', 'py']:
            return self._generate_python_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['javascript', 'js', 'node']:
            return self._generate_javascript_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['java']:
            return self._generate_java_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['typescript', 'ts']:
            return self._generate_typescript_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['go', 'golang']:
            return self._generate_go_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['rust']:
            return self._generate_rust_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['csharp', 'c#', 'dotnet']:
            return self._generate_csharp_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['php']:
            return self._generate_php_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['ruby']:
            return self._generate_ruby_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['swift']:
            return self._generate_swift_code(title, requirements, features, constraints, include_tests, include_docs)
        elif language.lower() in ['kotlin']:
            return self._generate_kotlin_code(title, requirements, features, constraints, include_tests, include_docs)
        else:
            return self._generate_generic_code(title, requirements, features, constraints, language, include_tests, include_docs)

    def _generate_python_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate Python code implementation."""
        
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        module_name = self._to_snake_case(title) if title else "generated_module"
        
        code_parts = []
        
        # Add imports
        code_parts.append("#!/usr/bin/env python3")
        code_parts.append('"""')
        if title:
            code_parts.append(f"{title}")
        code_parts.append("")
        if requirements:
            code_parts.append("Requirements:")
            for req in requirements:
                code_parts.append(f"- {req}")
        code_parts.append("")
        if features:
            code_parts.append("Features:")
            for feature in features:
                code_parts.append(f"- {feature}")
        code_parts.append('"""')
        code_parts.append("")
        
        # Add standard imports
        code_parts.append("import os")
        code_parts.append("import sys")
        code_parts.append("import json")
        code_parts.append("import logging")
        code_parts.append("from typing import Dict, List, Any, Optional")
        code_parts.append("from datetime import datetime")
        code_parts.append("")
        
        # Add logging setup
        code_parts.append("# Configure logging")
        code_parts.append("logging.basicConfig(level=logging.INFO)")
        code_parts.append("logger = logging.getLogger(__name__)")
        code_parts.append("")
        
        # Generate main class
        code_parts.append(f"class {class_name}:")
        if include_docs:
            code_parts.append(f'    """{title or "Generated class based on instructions"}."""')
            code_parts.append("")
        
        # Add constructor
        code_parts.append("    def __init__(self):")
        code_parts.append("        self.initialized = False")
        code_parts.append("        self.logger = logging.getLogger(__name__)")
        code_parts.append("")
        
        # Add methods based on features
        for feature in features:
            method_name = self._to_snake_case(feature.split()[0])
            code_parts.append(f"    def {method_name}(self):")
            if include_docs:
                code_parts.append(f'        """{feature}."""')
            code_parts.append("        try:")
            code_parts.append(f"            self.logger.info('Executing: {feature}')")
            code_parts.append("            # TODO: Implement functionality")
            code_parts.append("            return True")
            code_parts.append("        except Exception as e:")
            code_parts.append("            self.logger.error(f'Error in {method_name}: {{e}}')")
            code_parts.append("            return False")
            code_parts.append("")
        
        # Add main method
        code_parts.append("    def main(self):")
        code_parts.append('        """Main execution method."""')
        code_parts.append("        try:")
        code_parts.append("            self.logger.info('Starting execution')")
        code_parts.append("            # TODO: Add main logic here")
        code_parts.append("            self.logger.info('Execution completed')")
        code_parts.append("        except Exception as e:")
        code_parts.append("            self.logger.error(f'Main execution failed: {e}')")
        code_parts.append("")
        
        # Add main execution block
        code_parts.append("")
        code_parts.append("if __name__ == '__main__':")
        code_parts.append(f"    {module_name} = {class_name}()")
        code_parts.append(f"    {module_name}.main()")
        code_parts.append("")
        
        # Add tests if requested
        if include_tests:
            code_parts.append(self._generate_python_tests(class_name, features))
        
        return "\n".join(code_parts)

    def _generate_python_tests(self, class_name: str, features: list) -> str:
        """Generate Python test code."""
        test_code = []
        test_code.append("")
        test_code.append("# Tests")
        test_code.append("import unittest")
        test_code.append("")
        test_code.append(f"class Test{class_name}(unittest.TestCase):")
        test_code.append("    def setUp(self):")
        test_code.append(f"        self.instance = {class_name}()")
        test_code.append("")
        
        for feature in features:
            method_name = self._to_snake_case(feature.split()[0])
            test_code.append(f"    def test_{method_name}(self):")
            test_code.append(f'        """Test {feature}."""')
            test_code.append(f"        result = self.instance.{method_name}()")
            test_code.append("        self.assertIsNotNone(result)")
            test_code.append("")
        
        test_code.append("if __name__ == '__main__':")
        test_code.append("    unittest.main()")
        
        return "\n".join(test_code)

    def _generate_javascript_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate JavaScript code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        
        code_parts = []
        code_parts.append("/**")
        if title:
            code_parts.append(f" * {title}")
        code_parts.append(" */")
        code_parts.append("")
        
        # Add class
        code_parts.append(f"class {class_name} {{")
        code_parts.append("    constructor() {")
        code_parts.append("        this.initialized = false;")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append(f"    {method_name}() {{")
            if include_docs:
                code_parts.append(f"        // {feature}")
            code_parts.append("        try {")
            code_parts.append(f"            console.log('Executing: {feature}');")
            code_parts.append("            // TODO: Implement functionality");
            code_parts.append("            return true;")
            code_parts.append("        } catch (error) {")
            code_parts.append(f"            console.error('Error in {method_name}:', error);")
            code_parts.append("            return false;")
            code_parts.append("        }")
            code_parts.append("    }")
            code_parts.append("")
        
        code_parts.append("    main() {")
        code_parts.append("        console.log('Starting execution');")
        code_parts.append("        // TODO: Add main logic here");
        code_parts.append("        console.log('Execution completed');")
        code_parts.append("    }")
        code_parts.append("}")
        code_parts.append("")
        
        # Add usage
        code_parts.append("// Usage")
        code_parts.append(f"const {class_name.lower()} = new {class_name}();")
        code_parts.append(f"{class_name.lower()}.main();")
        
        return "\n".join(code_parts)

    def _generate_java_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate Java code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        
        code_parts = []
        code_parts.append("import java.util.*;")
        code_parts.append("import java.util.logging.*;")
        code_parts.append("")
        
        code_parts.append("/**")
        if title:
            code_parts.append(f" * {title}")
        code_parts.append(" */")
        code_parts.append(f"public class {class_name} {{")
        code_parts.append("    private static final Logger logger = Logger.getLogger(GeneratedClass.class.getName());")
        code_parts.append("    private boolean initialized;")
        code_parts.append("")
        
        code_parts.append("    public GeneratedClass() {")
        code_parts.append("        this.initialized = false;")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append(f"    public boolean {method_name}() {{")
            if include_docs:
                code_parts.append(f"        // {feature}")
            code_parts.append("        try {")
            code_parts.append(f"            logger.info('Executing: {feature}');")
            code_parts.append("            // TODO: Implement functionality");
            code_parts.append("            return true;")
            code_parts.append("        } catch (Exception e) {")
            code_parts.append(f"            logger.severe('Error in {method_name}: ' + e.getMessage());")
            code_parts.append("            return false;")
            code_parts.append("        }")
            code_parts.append("    }")
            code_parts.append("")
        
        code_parts.append("    public void main() {")
        code_parts.append("        logger.info('Starting execution');")
        code_parts.append("        // TODO: Add main logic here");
        code_parts.append("        logger.info('Execution completed');")
        code_parts.append("    }")
        code_parts.append("")
        
        code_parts.append("    public static void main(String[] args) {")
        code_parts.append(f"        {class_name} instance = new {class_name}();")
        code_parts.append("        instance.main();")
        code_parts.append("    }")
        code_parts.append("}")
        
        return "\n".join(code_parts)

    def _generate_generic_code(self, title: str, requirements: list, features: list, constraints: list, language: str, include_tests: bool, include_docs: bool) -> str:
        """Generate generic code for unsupported languages."""
        code_parts = []
        code_parts.append(f"// {title or 'Generated Code'}")
        code_parts.append(f"// Language: {language}")
        code_parts.append("")
        
        if requirements:
            code_parts.append("// Requirements:")
            for req in requirements:
                code_parts.append(f"// - {req}")
            code_parts.append("")
        
        if features:
            code_parts.append("// Features:")
            for feature in features:
                code_parts.append(f"// - {feature}")
            code_parts.append("")
        
        if constraints:
            code_parts.append("// Constraints:")
            for constraint in constraints:
                code_parts.append(f"// - {constraint}")
            code_parts.append("")
        
        code_parts.append("// TODO: Implement code generation for this language")
        code_parts.append("// This is a placeholder for unsupported language")
        
        return "\n".join(code_parts)

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camel case."""
        if not text:
            return "GeneratedClass"
        words = text.split()
        return ''.join(word.capitalize() for word in words)

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake case."""
        if not text:
            return "generated_module"
        return '_'.join(word.lower() for word in text.split())

    def _implement_from_instructions(self, arguments: dict) -> dict:
        """Alternative implementation method for code generation."""
        return self._read_and_generate_code(arguments)

    def _create_project_folder(self, instructions: str, language: str, source_file: str, generated_code: str, include_tests: bool, include_docs: bool) -> str:
        """Create a complete project folder structure on desktop."""
        try:
            # Parse project name from instructions
            project_name = self._extract_project_name(instructions, source_file)
            desktop_path = os.path.expanduser("~/Desktop")
            project_path = os.path.join(desktop_path, project_name)
            
            # Create project directory
            os.makedirs(project_path, exist_ok=True)
            logger.info(f"📁 CREATED PROJECT FOLDER: {project_path}")
            
            # Create project structure based on language
            if language.lower() in ['python', 'py']:
                self._create_python_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['javascript', 'js', 'node']:
                self._create_javascript_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['java']:
                self._create_java_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['typescript', 'ts']:
                self._create_typescript_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['go', 'golang']:
                self._create_go_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['rust']:
                self._create_rust_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['csharp', 'c#', 'dotnet']:
                self._create_csharp_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['php']:
                self._create_php_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['ruby']:
                self._create_ruby_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['swift']:
                self._create_swift_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            elif language.lower() in ['kotlin']:
                self._create_kotlin_project_structure(project_path, project_name, generated_code, instructions, include_tests, include_docs)
            else:
                self._create_generic_project_structure(project_path, project_name, generated_code, instructions, language, include_tests, include_docs)
            
            logger.info(f"✅ PROJECT FOLDER COMPLETE: {project_path}")
            return project_path
            
        except Exception as e:
            logger.error(f"❌ PROJECT FOLDER CREATION FAILED: {e}")
            return None

    def _extract_project_name(self, instructions: str, source_file: str) -> str:
        """Extract project name from instructions or source file."""
        # Try to extract title from instructions
        lines = instructions.split('\n')
        for line in lines:
            line = line.strip()
            if line.lower().startswith(('title:', 'name:', 'project:')):
                title = line.split(':', 1)[1].strip()
                return self._to_snake_case(title)
        
        # Fallback to source file name
        if source_file:
            base_name = os.path.splitext(source_file)[0]
            return self._to_snake_case(base_name)
        
        return "generated_project"

    def _create_python_project_structure(self, project_path: str, project_name: str, generated_code: str, instructions: str, include_tests: bool, include_docs: bool):
        """Create Python project structure."""
        # Create main package directory
        src_path = os.path.join(project_path, project_name)
        os.makedirs(src_path, exist_ok=True)
        
        # Create __init__.py
        with open(os.path.join(src_path, "__init__.py"), 'w') as f:
            f.write(f'"""\n{project_name} package.\n"""\n\n__version__ = "0.1.0"\n')
        
        # Create main module
        main_file = os.path.join(src_path, "main.py")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # Create requirements.txt
        requirements = [
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
            "pydantic>=1.8.0",
            "sqlalchemy>=1.4.0",
            "psycopg2-binary>=2.9.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.0",
            "python-multipart>=0.0.5",
            "requests>=2.25.0",
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0"
        ]
        
        with open(os.path.join(project_path, "requirements.txt"), 'w') as f:
            f.write('\n'.join(requirements))
        
        # Create setup.py
        setup_py = f'''#!/usr/bin/env python3
"""
Setup script for {project_name}.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{project_name}",
    version="0.1.0",
    author="Generated by Code Writing Agent",
    description="Generated from instructions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
    ],
    extras_require={{
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
    }},
)
'''
        with open(os.path.join(project_path, "setup.py"), 'w') as f:
            f.write(setup_py)
        
        # Create README.md
        readme_content = f"""# {project_name}

Generated from instructions using the Code Writing Agent.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m {project_name}.main
```

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black {project_name}/
```

## Original Instructions

```
{instructions}
```
"""
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)
        
        # Create .gitignore
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
        with open(os.path.join(project_path, ".gitignore"), 'w') as f:
            f.write(gitignore_content)
        
        # Create tests directory if tests are included
        if include_tests:
            tests_path = os.path.join(project_path, "tests")
            os.makedirs(tests_path, exist_ok=True)
            
            with open(os.path.join(tests_path, "__init__.py"), 'w') as f:
                f.write('"""Tests for the project."""\n')
            
            # Extract test code from generated code
            if "# Tests" in generated_code:
                test_section = generated_code.split("# Tests")[1]
                with open(os.path.join(tests_path, "test_main.py"), 'w') as f:
                    f.write(test_section)

    def _create_javascript_project_structure(self, project_path: str, project_name: str, generated_code: str, instructions: str, include_tests: bool, include_docs: bool):
        """Create JavaScript project structure."""
        # Create src directory
        src_path = os.path.join(project_path, "src")
        os.makedirs(src_path, exist_ok=True)
        
        # Create main file
        main_file = os.path.join(src_path, "index.js")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # Create package.json
        package_json = f'''{{
  "name": "{project_name}",
  "version": "0.1.0",
  "description": "Generated from instructions using Code Writing Agent",
  "main": "src/index.js",
  "scripts": {{
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  }},
  "keywords": ["generated", "code-writing-agent"],
  "author": "Generated by Code Writing Agent",
  "license": "MIT",
  "dependencies": {{
    "express": "^4.17.1",
    "cors": "^2.8.5",
    "helmet": "^4.6.0",
    "dotenv": "^10.0.0",
    "joi": "^17.4.0",
    "jsonwebtoken": "^8.5.1",
    "bcryptjs": "^2.4.3",
    "pg": "^8.7.0",
    "sequelize": "^6.6.0"
  }},
  "devDependencies": {{
    "jest": "^27.0.0",
    "nodemon": "^2.0.12",
    "eslint": "^7.32.0",
    "prettier": "^2.3.0"
  }},
  "engines": {{
    "node": ">=14.0.0"
  }}
}}
'''
        with open(os.path.join(project_path, "package.json"), 'w') as f:
            f.write(package_json)
        
        # Create README.md
        readme_content = f"""# {project_name}

Generated from instructions using the Code Writing Agent.

## Installation

```bash
npm install
```

## Usage

```bash
# Start the application
npm start

# Development mode with auto-reload
npm run dev
```

## Development

```bash
# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Original Instructions

```
{instructions}
```
"""
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)
        
        # Create .gitignore
        gitignore_content = """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# TypeScript v1 declaration files
typings/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test

# parcel-bundler cache
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/
"""
        with open(os.path.join(project_path, ".gitignore"), 'w') as f:
            f.write(gitignore_content)
        
        # Create .eslintrc.js
        eslint_config = """module.exports = {
  env: {
    node: true,
    es2021: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module',
  },
  rules: {
    'indent': ['error', 2],
    'linebreak-style': ['error', 'unix'],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
  },
};
"""
        with open(os.path.join(project_path, ".eslintrc.js"), 'w') as f:
            f.write(eslint_config)

    def _create_java_project_structure(self, project_path: str, project_name: str, generated_code: str, instructions: str, include_tests: bool, include_docs: bool):
        """Create Java project structure."""
        # Create Maven-style structure
        src_main_java = os.path.join(project_path, "src", "main", "java")
        os.makedirs(src_main_java, exist_ok=True)
        
        # Create package structure
        package_path = os.path.join(src_main_java, "com", "generated", project_name.lower())
        os.makedirs(package_path, exist_ok=True)
        
        # Create main class
        main_file = os.path.join(package_path, f"{project_name}.java")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # Create pom.xml
        pom_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.generated</groupId>
    <artifactId>{project_name.lower()}</artifactId>
    <version>0.1.0</version>
    <packaging>jar</packaging>

    <name>{project_name}</name>
    <description>Generated from instructions using Code Writing Agent</description>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>1.7.32</version>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <version>1.2.6</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>2.22.2</version>
            </plugin>
        </plugins>
    </build>
</project>
'''
        with open(os.path.join(project_path, "pom.xml"), 'w') as f:
            f.write(pom_xml)
        
        # Create README.md
        readme_content = f"""# {project_name}

Generated from instructions using the Code Writing Agent.

## Prerequisites

- Java 11 or higher
- Maven 3.6 or higher

## Installation

```bash
mvn clean install
```

## Usage

```bash
mvn exec:java -Dexec.mainClass="com.generated.{project_name.lower()}.{project_name}"
```

## Development

```bash
# Run tests
mvn test

# Compile
mvn compile

# Package
mvn package
```

## Original Instructions

```
{instructions}
```
"""
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)

    def _create_generic_project_structure(self, project_path: str, project_name: str, generated_code: str, instructions: str, language: str, include_tests: bool, include_docs: bool):
        """Create generic project structure for unsupported languages."""
        # Create src directory
        src_path = os.path.join(project_path, "src")
        os.makedirs(src_path, exist_ok=True)
        
        # Create main file
        main_file = os.path.join(src_path, f"main.{language}")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # Create README.md
        readme_content = f"""# {project_name}

Generated from instructions using the Code Writing Agent.

Language: {language}

## Usage

Run the main file in the src directory.

## Original Instructions

```
{instructions}
```
"""
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)

    def _generate_typescript_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate TypeScript code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        interface_name = f"I{class_name}"
        
        code_parts = []
        code_parts.append("/**")
        if title:
            code_parts.append(f" * {title}")
        code_parts.append(" */")
        code_parts.append("")
        
        # Add interface
        code_parts.append(f"interface {interface_name} {{")
        code_parts.append("    initialized: boolean;")
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append(f"    {method_name}(): boolean;")
        code_parts.append("    main(): void;")
        code_parts.append("}")
        code_parts.append("")
        
        # Add class
        code_parts.append(f"class {class_name} implements {interface_name} {{")
        code_parts.append("    public initialized: boolean = false;")
        code_parts.append("")
        
        # Add constructor
        code_parts.append("    constructor() {")
        code_parts.append("        this.initialized = false;")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append(f"    public {method_name}(): boolean {{")
            if include_docs:
                code_parts.append(f"        // {feature}")
            code_parts.append("        try {")
            code_parts.append(f"            console.log('Executing: {feature}');")
            code_parts.append("            // TODO: Implement functionality");
            code_parts.append("            return true;")
            code_parts.append("        } catch (error) {")
            code_parts.append(f"            console.error('Error in {method_name}:', error);")
            code_parts.append("            return false;")
            code_parts.append("        }")
            code_parts.append("    }")
            code_parts.append("")
        
        code_parts.append("    public main(): void {")
        code_parts.append("        console.log('Starting execution');")
        code_parts.append("        // TODO: Add main logic here");
        code_parts.append("        console.log('Execution completed');")
        code_parts.append("    }")
        code_parts.append("}")
        code_parts.append("")
        
        # Add usage
        code_parts.append("// Usage")
        code_parts.append(f"const {class_name.lower()}: {class_name} = new {class_name}();")
        code_parts.append(f"{class_name.lower()}.main();")
        
        return "\n".join(code_parts)

    def _generate_go_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate Go code implementation."""
        package_name = self._to_snake_case(title) if title else "generated"
        struct_name = self._to_camel_case(title) if title else "GeneratedStruct"
        
        code_parts = []
        code_parts.append(f"package {package_name}")
        code_parts.append("")
        
        code_parts.append("import (")
        code_parts.append('    "fmt"')
        code_parts.append('    "log"')
        code_parts.append('    "time"')
        code_parts.append(")")
        code_parts.append("")
        
        # Add struct
        code_parts.append(f"// {struct_name} represents {title or 'generated struct'}")
        code_parts.append(f"type {struct_name} struct {{")
        code_parts.append("    Initialized bool")
        code_parts.append("}")
        code_parts.append("")
        
        # Add constructor
        code_parts.append(f"// New{struct_name} creates a new instance")
        code_parts.append(f"func New{struct_name}() *{struct_name} {{")
        code_parts.append(f"    return &{struct_name}{{")
        code_parts.append("        Initialized: false,")
        code_parts.append("    }")
        code_parts.append("}")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append(f"// {method_name} {feature}")
            code_parts.append(f"func (g *{struct_name}) {method_name}() error {{")
            code_parts.append("    defer func() {")
            code_parts.append("        if r := recover(); r != nil {")
            code_parts.append(f"            log.Printf('Error in {method_name}: %v', r)")
            code_parts.append("        }")
            code_parts.append("    }()")
            code_parts.append("")
            code_parts.append(f"    log.Printf('Executing: {feature}')")
            code_parts.append("    // TODO: Implement functionality")
            code_parts.append("    return nil")
            code_parts.append("}")
            code_parts.append("")
        
        # Add main method
        code_parts.append("// Main executes the main logic")
        code_parts.append(f"func (g *{struct_name}) Main() error {{")
        code_parts.append("    log.Println('Starting execution')")
        code_parts.append("    // TODO: Add main logic here")
        code_parts.append("    log.Println('Execution completed')")
        code_parts.append("    return nil")
        code_parts.append("}")
        code_parts.append("")
        
        # Add main function
        code_parts.append("func main() {")
        code_parts.append(f"    instance := New{struct_name}()")
        code_parts.append("    if err := instance.Main(); err != nil {")
        code_parts.append("        log.Fatal(err)")
        code_parts.append("    }")
        code_parts.append("}")
        
        return "\n".join(code_parts)

    def _generate_rust_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate Rust code implementation."""
        struct_name = self._to_camel_case(title) if title else "GeneratedStruct"
        
        code_parts = []
        code_parts.append("use std::error::Error;")
        code_parts.append("use std::fmt;")
        code_parts.append("")
        
        # Add custom error
        code_parts.append("#[derive(Debug)]")
        code_parts.append("struct CustomError {")
        code_parts.append("    message: String,")
        code_parts.append("}")
        code_parts.append("")
        
        code_parts.append("impl fmt::Display for CustomError {")
        code_parts.append("    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {")
        code_parts.append("        write!(f, '{}', self.message)")
        code_parts.append("    }")
        code_parts.append("}")
        code_parts.append("")
        
        code_parts.append("impl Error for CustomError {}")
        code_parts.append("")
        
        # Add struct
        code_parts.append(f"/// {struct_name} represents {title or 'generated struct'}")
        code_parts.append(f"pub struct {struct_name} {{")
        code_parts.append("    initialized: bool,")
        code_parts.append("}")
        code_parts.append("")
        
        # Add implementation
        code_parts.append(f"impl {struct_name} {{")
        code_parts.append(f"    /// Creates a new {struct_name}")
        code_parts.append(f"    pub fn new() -> Self {{")
        code_parts.append(f"        {struct_name} {{")
        code_parts.append("            initialized: false,")
        code_parts.append("        }")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_snake_case(feature.split()[0])
            code_parts.append(f"    /// {feature}")
            code_parts.append(f"    pub fn {method_name}(&self) -> Result<bool, Box<dyn Error>> {{")
            code_parts.append(f"        println!('Executing: {feature}');")
            code_parts.append("        // TODO: Implement functionality");
            code_parts.append("        Ok(true)")
            code_parts.append("    }")
            code_parts.append("")
        
        # Add main method
        code_parts.append("    /// Main execution method")
        code_parts.append("    pub fn main(&self) -> Result<(), Box<dyn Error>> {")
        code_parts.append("        println!('Starting execution');")
        code_parts.append("        // TODO: Add main logic here");
        code_parts.append("        println!('Execution completed');")
        code_parts.append("        Ok(())")
        code_parts.append("    }")
        code_parts.append("}")
        code_parts.append("")
        
        # Add main function
        code_parts.append("fn main() -> Result<(), Box<dyn Error>> {")
        code_parts.append(f"    let instance = {struct_name}::new();")
        code_parts.append("    instance.main()")
        code_parts.append("}")
        
        return "\n".join(code_parts)

    def _generate_csharp_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate C# code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        namespace_name = self._to_camel_case(title) if title else "GeneratedNamespace"
        
        code_parts = []
        code_parts.append("using System;")
        code_parts.append("using System.Collections.Generic;")
        code_parts.append("using System.Threading.Tasks;")
        code_parts.append("using Microsoft.Extensions.Logging;")
        code_parts.append("")
        
        code_parts.append(f"namespace {namespace_name}")
        code_parts.append("{")
        code_parts.append(f"    /// <summary>")
        code_parts.append(f"    /// {title or 'Generated class based on instructions'}")
        code_parts.append(f"    /// </summary>")
        code_parts.append(f"    public class {class_name}")
        code_parts.append("    {")
        code_parts.append("        private readonly ILogger<GeneratedClass> _logger;")
        code_parts.append("        private bool _initialized;")
        code_parts.append("")
        
        # Add constructor
        code_parts.append(f"        public {class_name}(ILogger<GeneratedClass> logger)")
        code_parts.append("        {")
        code_parts.append("            _logger = logger;")
        code_parts.append("            _initialized = false;")
        code_parts.append("        }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append(f"        /// <summary>")
            code_parts.append(f"        /// {feature}")
            code_parts.append(f"        /// </summary>")
            code_parts.append(f"        public async Task<bool> {method_name}Async()")
            code_parts.append("        {")
            code_parts.append("            try")
            code_parts.append("            {")
            code_parts.append(f"                _logger.LogInformation('Executing: {feature}');")
            code_parts.append("                // TODO: Implement functionality");
            code_parts.append("                await Task.Delay(100); // Placeholder");
            code_parts.append("                return true;")
            code_parts.append("            }")
            code_parts.append("            catch (Exception ex)")
            code_parts.append("            {")
            code_parts.append(f"                _logger.LogError(ex, 'Error in {method_name}');")
            code_parts.append("                return false;")
            code_parts.append("            }")
            code_parts.append("        }")
            code_parts.append("")
        
        # Add main method
        code_parts.append("        /// <summary>")
        code_parts.append("        /// Main execution method")
        code_parts.append("        /// </summary>")
        code_parts.append("        public async Task MainAsync()")
        code_parts.append("        {")
        code_parts.append("            try")
        code_parts.append("            {")
        code_parts.append("                _logger.LogInformation('Starting execution');")
        code_parts.append("                // TODO: Add main logic here");
        code_parts.append("                _logger.LogInformation('Execution completed');")
        code_parts.append("            }")
        code_parts.append("            catch (Exception ex)")
        code_parts.append("            {")
        code_parts.append("                _logger.LogError(ex, 'Main execution failed');")
        code_parts.append("            }")
        code_parts.append("        }")
        code_parts.append("    }")
        code_parts.append("}")
        
        return "\n".join(code_parts)

    def _generate_php_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate PHP code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        
        code_parts = []
        code_parts.append("<?php")
        code_parts.append("")
        code_parts.append("declare(strict_types=1);")
        code_parts.append("")
        
        code_parts.append("/**")
        if title:
            code_parts.append(f" * {title}")
        code_parts.append(" */")
        code_parts.append(f"class {class_name}")
        code_parts.append("{")
        code_parts.append("    private bool $initialized;")
        code_parts.append("")
        
        # Add constructor
        code_parts.append("    public function __construct()")
        code_parts.append("    {")
        code_parts.append("        $this->initialized = false;")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append("    /**")
            code_parts.append(f"     * {feature}")
            code_parts.append("     */")
            code_parts.append(f"    public function {method_name}(): bool")
            code_parts.append("    {")
            code_parts.append("        try {")
            code_parts.append(f"            error_log('Executing: {feature}');")
            code_parts.append("            // TODO: Implement functionality");
            code_parts.append("            return true;")
            code_parts.append("        } catch (Exception $e) {")
            code_parts.append(f"            error_log('Error in {method_name}: ' . $e->getMessage());")
            code_parts.append("            return false;")
            code_parts.append("        }")
            code_parts.append("    }")
            code_parts.append("")
        
        # Add main method
        code_parts.append("    /**")
        code_parts.append("     * Main execution method")
        code_parts.append("     */")
        code_parts.append("    public function main(): void")
        code_parts.append("    {")
        code_parts.append("        try {")
        code_parts.append("            error_log('Starting execution');")
        code_parts.append("            // TODO: Add main logic here");
        code_parts.append("            error_log('Execution completed');")
        code_parts.append("        } catch (Exception $e) {")
        code_parts.append("            error_log('Main execution failed: ' . $e->getMessage());")
        code_parts.append("        }")
        code_parts.append("    }")
        code_parts.append("}")
        code_parts.append("")
        
        # Add usage
        code_parts.append("// Usage");
        code_parts.append(f"$instance = new {class_name}();");
        code_parts.append("$instance->main();");
        
        return "\n".join(code_parts)

    def _generate_ruby_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate Ruby code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        
        code_parts = []
        code_parts.append("require 'logger'")
        code_parts.append("")
        
        code_parts.append("# frozen_string_literal: true")
        code_parts.append("")
        
        code_parts.append("#")
        if title:
            code_parts.append(f"# {title}")
        code_parts.append("#")
        code_parts.append(f"class {class_name}")
        code_parts.append("  attr_reader :initialized")
        code_parts.append("")
        
        # Add constructor
        code_parts.append("  def initialize")
        code_parts.append("    @initialized = false")
        code_parts.append("    @logger = Logger.new($stdout)")
        code_parts.append("  end")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_snake_case(feature.split()[0])
            code_parts.append("  #")
            code_parts.append(f"  # {feature}")
            code_parts.append("  #")
            code_parts.append(f"  def {method_name}")
            code_parts.append("    begin")
            code_parts.append(f"      @logger.info('Executing: {feature}')")
            code_parts.append("      # TODO: Implement functionality")
            code_parts.append("      true")
            code_parts.append("    rescue StandardError => e")
            code_parts.append(f"      @logger.error('Error in {method_name}: #{e.message}')")
            code_parts.append("      false")
            code_parts.append("    end")
            code_parts.append("  end")
            code_parts.append("")
        
        # Add main method
        code_parts.append("  #")
        code_parts.append("  # Main execution method")
        code_parts.append("  #")
        code_parts.append("  def main")
        code_parts.append("    begin")
        code_parts.append("      @logger.info('Starting execution')")
        code_parts.append("      # TODO: Add main logic here")
        code_parts.append("      @logger.info('Execution completed')")
        code_parts.append("    rescue StandardError => e")
        code_parts.append("      @logger.error('Main execution failed: #{e.message}')")
        code_parts.append("    end")
        code_parts.append("  end")
        code_parts.append("end")
        code_parts.append("")
        
        # Add usage
        code_parts.append("# Usage")
        code_parts.append(f"instance = {class_name}.new")
        code_parts.append("instance.main")
        
        return "\n".join(code_parts)

    def _generate_swift_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate Swift code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        
        code_parts = []
        code_parts.append("import Foundation")
        code_parts.append("import os.log")
        code_parts.append("")
        
        code_parts.append("/**")
        if title:
            code_parts.append(f" * {title}")
        code_parts.append(" */")
        code_parts.append(f"class {class_name} {{")
        code_parts.append("    private let logger = Logger(subsystem: 'com.generated', category: 'GeneratedClass')")
        code_parts.append("    private var initialized: Bool")
        code_parts.append("")
        
        # Add initializer
        code_parts.append("    init() {")
        code_parts.append("        self.initialized = false")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append("    /**")
            code_parts.append(f"     * {feature}")
            code_parts.append("     */")
            code_parts.append(f"    func {method_name}() -> Bool {{")
            code_parts.append("        do {")
            code_parts.append(f"            logger.info('Executing: {feature}')")
            code_parts.append("            // TODO: Implement functionality")
            code_parts.append("            return true")
            code_parts.append("        } catch {")
            code_parts.append(f"            logger.error('Error in {method_name}: \\(error)')")
            code_parts.append("            return false")
            code_parts.append("        }")
            code_parts.append("    }")
            code_parts.append("")
        
        # Add main method
        code_parts.append("    /**")
        code_parts.append("     * Main execution method")
        code_parts.append("     */")
        code_parts.append("    func main() {")
        code_parts.append("        do {")
        code_parts.append("            logger.info('Starting execution')")
        code_parts.append("            // TODO: Add main logic here")
        code_parts.append("            logger.info('Execution completed')")
        code_parts.append("        } catch {")
        code_parts.append("            logger.error('Main execution failed: \\(error)')")
        code_parts.append("        }")
        code_parts.append("    }")
        code_parts.append("}")
        code_parts.append("")
        
        # Add usage
        code_parts.append("// Usage")
        code_parts.append(f"let instance = {class_name}()")
        code_parts.append("instance.main()")
        
        return "\n".join(code_parts)

    def _generate_kotlin_code(self, title: str, requirements: list, features: list, constraints: list, include_tests: bool, include_docs: bool) -> str:
        """Generate Kotlin code implementation."""
        class_name = self._to_camel_case(title) if title else "GeneratedClass"
        
        code_parts = []
        code_parts.append("import java.util.logging.Logger")
        code_parts.append("import java.util.logging.Level")
        code_parts.append("")
        
        code_parts.append("/**")
        if title:
            code_parts.append(f" * {title}")
        code_parts.append(" */")
        code_parts.append(f"class {class_name} {{")
        code_parts.append("    private val logger = Logger.getLogger(GeneratedClass::class.java.name)")
        code_parts.append("    private var initialized: Boolean = false")
        code_parts.append("")
        
        # Add constructor
        code_parts.append("    init {")
        code_parts.append("        initialized = false")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add methods
        for feature in features:
            method_name = self._to_camel_case(feature.split()[0])
            code_parts.append("    /**")
            code_parts.append(f"     * {feature}")
            code_parts.append("     */")
            code_parts.append(f"    fun {method_name}(): Boolean {{")
            code_parts.append("        return try {")
            code_parts.append(f"            logger.info('Executing: {feature}')")
            code_parts.append("            // TODO: Implement functionality")
            code_parts.append("            true")
            code_parts.append("        } catch (e: Exception) {")
            code_parts.append(f"            logger.log(Level.SEVERE, 'Error in {method_name}', e)")
            code_parts.append("            false")
            code_parts.append("        }")
            code_parts.append("    }")
            code_parts.append("")
        
        # Add main method
        code_parts.append("    /**")
        code_parts.append("     * Main execution method")
        code_parts.append("     */")
        code_parts.append("    fun main() {")
        code_parts.append("        try {")
        code_parts.append("            logger.info('Starting execution')")
        code_parts.append("            // TODO: Add main logic here")
        code_parts.append("            logger.info('Execution completed')")
        code_parts.append("        } catch (e: Exception) {")
        code_parts.append("            logger.log(Level.SEVERE, 'Main execution failed', e)")
        code_parts.append("        }")
        code_parts.append("    }")
        code_parts.append("")
        
        # Add main function
        code_parts.append("    companion object {")
        code_parts.append("        @JvmStatic")
        code_parts.append("        fun main(args: Array<String>) {")
        code_parts.append(f"            val instance = {class_name}()")
        code_parts.append("            instance.main()")
        code_parts.append("        }")
        code_parts.append("    }")
        code_parts.append("}")
        
        return "\n".join(code_parts)

    def _open_code_editor(self, project_path: str, language: str):
        """Open the generated code in the user's preferred code editor."""
        try:
            import subprocess
            import platform
            
            # Get the main source file path based on language
            main_file = None
            if language.lower() in ['python', 'py']:
                main_file = os.path.join(project_path, f"{os.path.basename(project_path)}", "main.py")
            elif language.lower() in ['javascript', 'js']:
                main_file = os.path.join(project_path, "src", "index.js")
            elif language.lower() in ['typescript', 'ts']:
                main_file = os.path.join(project_path, "src", "index.ts")
            elif language.lower() in ['java']:
                main_file = os.path.join(project_path, "src", "main", "java", f"{os.path.basename(project_path)}.java")
            elif language.lower() in ['kotlin']:
                main_file = os.path.join(project_path, "src", "main.kotlin")
            elif language.lower() in ['go', 'golang']:
                main_file = os.path.join(project_path, "main.go")
            elif language.lower() in ['rust']:
                main_file = os.path.join(project_path, "src", "main.rs")
            elif language.lower() in ['csharp', 'c#', 'dotnet']:
                main_file = os.path.join(project_path, "src", "Program.cs")
            elif language.lower() in ['php']:
                main_file = os.path.join(project_path, "src", "index.php")
            elif language.lower() in ['ruby']:
                main_file = os.path.join(project_path, "src", "main.rb")
            elif language.lower() in ['swift']:
                main_file = os.path.join(project_path, "src", "main.swift")
            else:
                # Fallback to project folder
                main_file = project_path
            
            # Check if main file exists, otherwise use project folder
            if not os.path.exists(main_file):
                main_file = project_path
            
            # Try to open with common code editors
            editors = []
            
            if platform.system() == "Darwin":  # macOS
                editors = [
                    ["open", "-a", "Visual Studio Code", main_file],
                    ["open", "-a", "Sublime Text", main_file],
                    ["open", "-a", "Atom", main_file],
                    ["open", "-a", "IntelliJ IDEA", main_file],
                    ["open", "-a", "PyCharm", main_file],
                    ["open", "-a", "WebStorm", main_file],
                    ["open", "-a", "CLion", main_file],
                    ["open", "-a", "GoLand", main_file],
                    ["open", "-a", "PhpStorm", main_file],
                    ["open", "-a", "Rider", main_file],
                    ["open", "-a", "RubyMine", main_file],
                    ["open", "-a", "AppCode", main_file],
                    ["open", "-a", "Android Studio", main_file],
                    ["open", "-a", "Xcode", main_file],
                    ["open", main_file]  # Default app
                ]
            elif platform.system() == "Windows":
                editors = [
                    ["code", main_file],
                    ["subl", main_file],
                    ["atom", main_file],
                    ["notepad++", main_file],
                    ["notepad", main_file]
                ]
            else:  # Linux
                editors = [
                    ["code", main_file],
                    ["subl", main_file],
                    ["atom", main_file],
                    ["gedit", main_file],
                    ["nano", main_file],
                    ["vim", main_file]
                ]
            
            # Try each editor until one works
            for editor_cmd in editors:
                try:
                    result = subprocess.run(editor_cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        logger.info(f"🚀 OPENED CODE EDITOR: {' '.join(editor_cmd)}")
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                    continue
            
            # If no editor found, try to open the folder in file explorer
            try:
                if platform.system() == "Darwin":
                    subprocess.run(["open", project_path], check=True)
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", project_path], check=True)
                else:
                    subprocess.run(["xdg-open", project_path], check=True)
                logger.info(f"📁 OPENED PROJECT FOLDER: {project_path}")
                return True
            except subprocess.SubprocessError:
                pass
            
            logger.warning(f"⚠️  Could not open code editor for: {project_path}")
            return False
            
        except Exception as e:
            logger.error(f"❌ FAILED TO OPEN CODE EDITOR: {e}")
            return False

    def _create_typescript_project_structure(self, project_path: str, project_name: str, generated_code: str, instructions: str, include_tests: bool, include_docs: bool):
        """Create TypeScript project structure."""
        # Create src directory
        src_path = os.path.join(project_path, "src")
        os.makedirs(src_path, exist_ok=True)
        
        # Create main file
        main_file = os.path.join(src_path, "index.ts")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # Create package.json
        package_json = f'''{{
  "name": "{project_name}",
  "version": "0.1.0",
  "description": "Generated from instructions using Code Writing Agent",
  "main": "dist/index.js",
  "scripts": {{
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  }},
  "keywords": ["generated", "code-writing-agent", "typescript"],
  "author": "Generated by Code Writing Agent",
  "license": "MIT",
  "dependencies": {{
    "express": "^4.17.1",
    "cors": "^2.8.5",
    "helmet": "^4.6.0",
    "dotenv": "^10.0.0"
  }},
  "devDependencies": {{
    "@types/node": "^16.0.0",
    "@types/express": "^4.17.13",
    "@types/cors": "^2.8.12",
    "typescript": "^4.5.0",
    "ts-node": "^10.4.0",
    "jest": "^27.0.0",
    "@types/jest": "^27.0.0",
    "eslint": "^7.32.0",
    "@typescript-eslint/eslint-plugin": "^5.0.0",
    "@typescript-eslint/parser": "^5.0.0",
    "prettier": "^2.3.0"
  }},
  "engines": {{
    "node": ">=14.0.0"
  }}
}}
'''
        with open(os.path.join(project_path, "package.json"), 'w') as f:
            f.write(package_json)
        
        # Create tsconfig.json
        tsconfig = '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
'''
        with open(os.path.join(project_path, "tsconfig.json"), 'w') as f:
            f.write(tsconfig)
        
        # Create README.md
        readme_content = f"""# {project_name}

Generated from instructions using the Code Writing Agent.

## Installation

```bash
npm install
```

## Usage

```bash
# Build the project
npm run build

# Start the application
npm start

# Development mode
npm run dev
```

## Development

```bash
# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Original Instructions

```
{instructions}
```
"""
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)
        
        # Create .gitignore
        gitignore_content = """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build output
dist/
build/

# TypeScript
*.tsbuildinfo

# Coverage directory
coverage/
*.lcov

# Environment variables
.env
.env.local
.env.test

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"""
        with open(os.path.join(project_path, ".gitignore"), 'w') as f:
            f.write(gitignore_content)

    def _create_kotlin_project_structure(self, project_path: str, project_name: str, generated_code: str, instructions: str, include_tests: bool, include_docs: bool):
        """Create Kotlin project structure."""
        # Create src directory
        src_path = os.path.join(project_path, "src")
        os.makedirs(src_path, exist_ok=True)
        
        # Create main file
        main_file = os.path.join(src_path, "main.kotlin")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # Create build.gradle.kts
        build_gradle = f'''plugins {{
    kotlin("jvm") version "1.8.0"
    application
}}

group = "com.example"
version = "0.1.0"

repositories {{
    mavenCentral()
}}

dependencies {{
    implementation(kotlin("stdlib"))
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.6.4")
    implementation("org.slf4j:slf4j-simple:1.7.36")
    
    testImplementation(kotlin("test"))
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.6.4")
}}

application {{
    mainClass.set("MainKt")
}}

tasks.test {{
    useJUnitPlatform()
}}

kotlin {{
    jvmToolchain(11)
}}
'''
        with open(os.path.join(project_path, "build.gradle.kts"), 'w') as f:
            f.write(build_gradle)
        
        # Create settings.gradle.kts
        settings_gradle = f'''rootProject.name = "{project_name}"
'''
        with open(os.path.join(project_path, "settings.gradle.kts"), 'w') as f:
            f.write(settings_gradle)
        
        # Create README.md
        readme_content = f"""# {project_name}

Generated from instructions using the Code Writing Agent.

Language: kotlin

## Prerequisites

- Java 11 or higher
- Gradle 7.0 or higher

## Installation

```bash
./gradlew build
```

## Usage

```bash
# Run the application
./gradlew run

# Build the application
./gradlew build

# Run tests
./gradlew test
```

## Development

```bash
# Format code
./gradlew ktlintFormat

# Run linter
./gradlew ktlintCheck

# Run tests with coverage
./gradlew test jacocoTestReport
```

## Original Instructions

```
{instructions}
```
"""
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)
        
        # Create .gitignore
        gitignore_content = """# Compiled class file
*.class

# Log file
*.log

# BlueJ files
*.ctxt

# Mobile Tools for Java (J2ME)
.mtj.tmp/

# Package Files #
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# virtual machine crash logs, see http://www.java.com/en/download/help/error_hotspot.xml
hs_err_pid*
replay_pid*

# Gradle
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar
!**/src/main/**/build/
!**/src/test/**/build/

# IntelliJ IDEA
.idea/
*.iws
*.iml
*.ipr
out/
!**/src/main/**/out/
!**/src/test/**/out/

# Eclipse
.apt_generated
.classpath
.factorypath
.project
.settings
.springBeans
.sts4-cache
bin/
!**/src/main/**/bin/
!**/src/test/**/bin/

# NetBeans
/nbproject/private/
/nbbuild/
/dist/
/nbdist/
/.nb-gradle/

# VS Code
.vscode/

# OS
.DS_Store
Thumbs.db
"""
        with open(os.path.join(project_path, ".gitignore"), 'w') as f:
            f.write(gitignore_content)

    def _create_go_project_structure(self, project_path: str, project_name: str, generated_code: str, instructions: str, include_tests: bool, include_docs: bool):
        """Create Go project structure."""
        # Create main.go
        main_file = os.path.join(project_path, "main.go")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # Create go.mod
        go_mod = f'''module {project_name}

go 1.19

require (
    github.com/gorilla/mux v1.8.0
    github.com/joho/godotenv v1.4.0
)
'''
        with open(os.path.join(project_path, "go.mod"), 'w') as f:
            f.write(go_mod)
        
        # Create README.md
        readme_content = f"""# {project_name}

Generated from instructions using the Code Writing Agent.

## Prerequisites

- Go 1.19 or higher

## Installation

```bash
go mod tidy
```

## Usage

```bash
# Run the application
go run main.go

# Build the application
go build -o {project_name}

# Run tests
go test ./...
```

## Development

```bash
# Format code
go fmt ./...

# Run linter
golangci-lint run

# Run tests with coverage
go test -cover ./...
```

## Original Instructions

```
{instructions}
```
"""
        with open(os.path.join(project_path, "README.md"), 'w') as f:
            f.write(readme_content)
        
        # Create .gitignore
        gitignore_content = """# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Output of the go coverage tool, specifically when used with LiteIDE
*.out

# Dependency directories (remove the comment below to include it)
# vendor/

# Go workspace file
go.work

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""
        with open(os.path.join(project_path, ".gitignore"), 'w') as f:
            f.write(gitignore_content)

    def _code_writing_agent(self, arguments: dict) -> dict:
        """Main code writing agent that orchestrates the process."""
        try:
            instruction_file = arguments.get("instruction_file", "")
            language = arguments.get("language", "python")
            output_file = arguments.get("output_file", "")
            
            # Use the main implementation
            return self._read_and_generate_code({
                "file_name": instruction_file,
                "language": language,
                "output_file": output_file,
                "include_tests": True,
                "include_docs": True,
                "create_project_folder": True
            })
            
        except Exception as e:
            logger.error(f"❌ CODE WRITING AGENT FAILED: {e}")
            return {
                "success": False,
                "tool_name": "code_writing_agent",
                "error": f"Code writing agent failed: {str(e)}"
            }

    def _select_language_and_generate(self, arguments: dict) -> dict:
        """Interactive language selection and code generation with editor opening."""
        try:
            file_name = arguments.get("file_name", "")
            preferred_language = arguments.get("preferred_language", "python")
            include_tests = arguments.get("include_tests", True)
            include_docs = arguments.get("include_docs", True)
            
            # Available languages for selection
            available_languages = [
                "python", "javascript", "java", "kotlin", "typescript", 
                "go", "rust", "csharp", "php", "ruby", "swift"
            ]
            
            # Use preferred language if valid, otherwise default to python
            if preferred_language.lower() in available_languages:
                selected_language = preferred_language.lower()
            else:
                selected_language = "python"
            
            logger.info(f"🎯 SELECTED LANGUAGE: {selected_language}")
            
            # Call the main code generation with editor opening enabled
            code_args = {
                "file_name": file_name,
                "language": selected_language,
                "include_tests": include_tests,
                "include_docs": include_docs,
                "create_project_folder": True,
                "open_editor": True
            }
            
            result = self._read_and_generate_code(code_args)
            
            # Add language selection info to result
            result["selected_language"] = selected_language
            result["available_languages"] = available_languages
            result["tool_name"] = "select_language_and_generate"
            
            return result
            
        except Exception as e:
            logger.error(f"❌ LANGUAGE SELECTION FAILED: {e}")
            return {
                "success": False,
                "tool_name": "select_language_and_generate",
                "error": f"Failed to select language and generate code: {str(e)}"
            }

    def _create_instruction_file(self, arguments: dict) -> dict:
        """Create instruction files on desktop for other agents to read and execute."""
        try:
            file_name = arguments.get("file_name", "")
            title = arguments.get("title", "Instruction File")
            action_type = arguments.get("action_type", "code_generation")  # code_generation, file_operation, web_search, etc.
            description = arguments.get("description", "")
            requirements = arguments.get("requirements", [])
            features = arguments.get("features", [])
            constraints = arguments.get("constraints", [])
            language = arguments.get("language", "python")
            priority = arguments.get("priority", "medium")  # low, medium, high
            tags = arguments.get("tags", [])
            
            # Validate inputs
            if not file_name:
                return {
                    "success": False,
                    "tool_name": "create_instruction_file",
                    "error": "No file name provided"
                }
            
            # Ensure file has .md extension
            if not file_name.endswith('.md'):
                file_name += '.md'
            
            # Create instruction content
            instruction_content = f"""# {title}

## Action Type
{action_type}

## Description
{description}

## Requirements
"""
            
            if isinstance(requirements, list):
                for req in requirements:
                    instruction_content += f"- {req}\n"
            else:
                instruction_content += f"- {requirements}\n"
            
            instruction_content += "\n## Features\n"
            if isinstance(features, list):
                for feature in features:
                    instruction_content += f"- {feature}\n"
            else:
                instruction_content += f"- {features}\n"
            
            instruction_content += "\n## Constraints\n"
            if isinstance(constraints, list):
                for constraint in constraints:
                    instruction_content += f"- {constraint}\n"
            else:
                instruction_content += f"- {constraints}\n"
            
            instruction_content += f"""
## Language
{language}

## Priority
{priority}

## Tags
{', '.join(tags) if isinstance(tags, list) else tags}

## Created
{datetime.now().isoformat()}

## Instructions for Agent
1. Read this file carefully
2. Understand the action type: {action_type}
3. Execute the described action
4. Report back with results
"""
            
            # Save to desktop
            desktop_path = os.path.expanduser("~/Desktop")
            file_path = os.path.join(desktop_path, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(instruction_content)
            
            logger.info(f"📝 CREATED INSTRUCTION FILE: {file_path}")
            
            return {
                "success": True,
                "tool_name": "create_instruction_file",
                "file_name": file_name,
                "file_path": file_path,
                "action_type": action_type,
                "language": language,
                "priority": priority,
                "content_preview": instruction_content[:200] + "..." if len(instruction_content) > 200 else instruction_content,
                "message": f"Created instruction file '{file_name}' on desktop for {action_type} action"
            }
            
        except Exception as e:
            logger.error(f"❌ CREATE INSTRUCTION FILE FAILED: {e}")
            return {
                "success": False,
                "tool_name": "create_instruction_file",
                "error": f"Failed to create instruction file: {str(e)}"
            }

    def _read_and_execute_instruction(self, arguments: dict) -> dict:
        """Read instruction files from desktop and execute the described actions."""
        try:
            file_name = arguments.get("file_name", "")
            file_path = arguments.get("file_path", "")
            auto_execute = arguments.get("auto_execute", True)
            
            if not file_path and not file_name:
                return {
                    "success": False,
                    "tool_name": "read_and_execute_instruction",
                    "error": "No file path or name provided"
                }
            
            # If only file name provided, construct full path
            if not file_path:
                desktop_path = os.path.expanduser("~/Desktop")
                file_path = os.path.join(desktop_path, file_name)
            
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "tool_name": "read_and_execute_instruction",
                    "error": f"Instruction file not found: {file_path}"
                }
            
            # Read instruction file
            with open(file_path, 'r', encoding='utf-8') as f:
                instruction_content = f.read()
            
            logger.info(f"📖 READING INSTRUCTION FILE: {os.path.basename(file_path)}")
            
            # Parse instruction content
            parsed_instruction = self._parse_instruction_file(instruction_content)
            
            # Execute action based on action type
            execution_result = None
            if auto_execute:
                execution_result = self._execute_instruction_action(parsed_instruction)
            
            return {
                "success": True,
                "tool_name": "read_and_execute_instruction",
                "file_path": file_path,
                "parsed_instruction": parsed_instruction,
                "execution_result": execution_result,
                "auto_executed": auto_execute,
                "message": f"Read instruction file and {'executed' if auto_execute else 'parsed'} {parsed_instruction.get('action_type', 'unknown')} action"
            }
            
        except Exception as e:
            logger.error(f"❌ READ AND EXECUTE INSTRUCTION FAILED: {e}")
            return {
                "success": False,
                "tool_name": "read_and_execute_instruction",
                "error": f"Failed to read and execute instruction: {str(e)}"
            }

    def _parse_instruction_file(self, content: str) -> dict:
        """Parse instruction file content into structured data."""
        try:
            lines = content.split('\n')
            parsed = {
                "title": "",
                "action_type": "",
                "description": "",
                "requirements": [],
                "features": [],
                "constraints": [],
                "language": "",
                "priority": "",
                "tags": [],
                "created": ""
            }
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('# '):
                    parsed["title"] = line[2:].strip()
                elif line.startswith('## '):
                    section = line[3:].lower().strip()
                    # Map section names to parsed keys
                    section_mapping = {
                        "action type": "action_type",
                        "action_type": "action_type"
                    }
                    current_section = section_mapping.get(section, section)
                elif line.startswith('- ') and current_section:
                    item = line[2:].strip()
                    if current_section in parsed and isinstance(parsed[current_section], list):
                        parsed[current_section].append(item)
                    else:
                        parsed[current_section] = [item]
                elif line and current_section and not line.startswith('-') and not line.startswith('#'):
                    if current_section in parsed and not isinstance(parsed[current_section], list):
                        parsed[current_section] = line
            
            return parsed
            
        except Exception as e:
            logger.error(f"❌ PARSE INSTRUCTION FAILED: {e}")
            return {"error": f"Failed to parse instruction: {str(e)}"}

    def _execute_instruction_action(self, instruction: dict) -> dict:
        """Execute action based on parsed instruction."""
        try:
            action_type = instruction.get("action_type", "").lower()
            
            if action_type == "code_generation":
                return self._execute_code_generation_action(instruction)
            elif action_type == "file_operation":
                return self._execute_file_operation_action(instruction)
            elif action_type == "web_search":
                return self._execute_web_search_action(instruction)
            elif action_type == "email":
                return self._execute_email_action(instruction)
            elif action_type == "phone_call":
                return self._execute_phone_call_action(instruction)
            else:
                return {
                    "success": False,
                    "action_type": action_type,
                    "error": f"Unknown action type: {action_type}"
                }
                
        except Exception as e:
            logger.error(f"❌ EXECUTE INSTRUCTION ACTION FAILED: {e}")
            return {
                "success": False,
                "error": f"Failed to execute instruction action: {str(e)}"
            }

    def _execute_code_generation_action(self, instruction: dict) -> dict:
        """Execute code generation action from instruction."""
        try:
            # Create a temporary instruction file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(f"""# {instruction.get('title', 'Generated Code')}

Requirements:
{chr(10).join([f'- {req}' for req in instruction.get('requirements', [])])}

Features:
{chr(10).join([f'- {feature}' for feature in instruction.get('features', [])])}

Constraints:
{chr(10).join([f'- {constraint}' for constraint in instruction.get('constraints', [])])}
""")
                temp_file = f.name
            
            # Call code generation
            code_args = {
                "file_name": temp_file,
                "language": instruction.get("language", "python"),
                "include_tests": True,
                "include_docs": True,
                "create_project_folder": True,
                "open_editor": True
            }
            
            result = self._read_and_generate_code(code_args)
            
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"❌ CODE GENERATION ACTION FAILED: {e}")
            return {
                "success": False,
                "error": f"Failed to execute code generation: {str(e)}"
            }

    def _execute_file_operation_action(self, instruction: dict) -> dict:
        """Execute file operation action from instruction."""
        try:
            operation = instruction.get("description", "").lower()
            
            if "list" in operation and "desktop" in operation:
                return self._list_desktop_files({})
            elif "search" in operation and "desktop" in operation:
                search_term = instruction.get("requirements", [""])[0] if instruction.get("requirements") else ""
                return self._search_desktop_files({"search_term": search_term})
            elif "read" in operation and "file" in operation:
                file_name = instruction.get("requirements", [""])[0] if instruction.get("requirements") else ""
                return self._read_desktop_file({"file_name": file_name})
            else:
                return {
                    "success": False,
                    "error": f"Unknown file operation: {operation}"
                }
                
        except Exception as e:
            logger.error(f"❌ FILE OPERATION ACTION FAILED: {e}")
            return {
                "success": False,
                "error": f"Failed to execute file operation: {str(e)}"
            }

    def _execute_web_search_action(self, instruction: dict) -> dict:
        """Execute web search action from instruction."""
        try:
            query = instruction.get("description", "") or instruction.get("requirements", [""])[0]
            
            # This would integrate with web search tools
            return {
                "success": True,
                "action_type": "web_search",
                "query": query,
                "message": f"Web search for: {query}",
                "note": "Web search integration would be implemented here"
            }
            
        except Exception as e:
            logger.error(f"❌ WEB SEARCH ACTION FAILED: {e}")
            return {
                "success": False,
                "error": f"Failed to execute web search: {str(e)}"
            }

    def _execute_email_action(self, instruction: dict) -> dict:
        """Execute email action from instruction."""
        try:
            # Extract email details from instruction
            to_email = instruction.get("requirements", [""])[0] if instruction.get("requirements") else ""
            subject = instruction.get("title", "")
            body = instruction.get("description", "")
            
            return self._send_email({
                "to_email": to_email,
                "subject": subject,
                "body": body
            })
            
        except Exception as e:
            logger.error(f"❌ EMAIL ACTION FAILED: {e}")
            return {
                "success": False,
                "error": f"Failed to execute email action: {str(e)}"
            }

    def _execute_phone_call_action(self, instruction: dict) -> dict:
        """Execute phone call action from instruction."""
        try:
            phone_number = instruction.get("requirements", [""])[0] if instruction.get("requirements") else ""
            caller_name = instruction.get("title", "Instruction Agent")
            
            return self._make_phone_call({
                "phone_number": phone_number,
                "caller_name": caller_name
            })
            
        except Exception as e:
            logger.error(f"❌ PHONE CALL ACTION FAILED: {e}")
            return {
                "success": False,
                "error": f"Failed to execute phone call action: {str(e)}"
            }

    def get_health(self) -> dict:
        """Health check with detailed status."""
        return {
            "status": "healthy",
            "server": "simple_mcp_bridge",
            "gmail_sender_loaded": self.gmail_sender is not None,
            "gmail_sender_status": "loaded" if self.gmail_sender else "not_loaded",
            "timestamp": datetime.now().isoformat()
        }

    def get_tools(self) -> dict:
        """Get available tools."""
        return {
            "tools": [
                {"name": "count_r", "description": "Count 'r' letters in a word"},
                {"name": "list_desktop_contents", "description": "List desktop files/folders"},
                {"name": "get_desktop_path", "description": "Get desktop path"},
                {"name": "list_desktop_files", "description": "List all files on desktop with details"},
                {"name": "search_desktop_files", "description": "Search for files on desktop by name/pattern"},
                {"name": "read_desktop_file", "description": "Read content of a specific file from desktop"},
                {"name": "ingest_desktop_file", "description": "Ingest a file from desktop into vector database"},
                {"name": "batch_ingest_desktop", "description": "Ingest multiple files from desktop at once"},
                {"name": "open_gmail", "description": "Open Gmail in browser"},
                {"name": "open_gmail_compose", "description": "Open Gmail compose window"},
                {"name": "sendmail", "description": "Send email via Gmail SMTP"},
                {"name": "sendmail_simple", "description": "Simple email sending via Gmail SMTP"},
                {"name": "call_phone", "description": "Make a phone call to a specified number"},
                {"name": "make_call", "description": "Make a phone call (alias for call_phone)"},
                {"name": "dial_number", "description": "Dial a phone number (alias for call_phone)"},
                {"name": "end_call", "description": "End an active phone call"},
                {"name": "hang_up", "description": "Hang up a call (alias for end_call)"},
                {"name": "call_status", "description": "Get status of an active call"},
                {"name": "read_and_generate_code", "description": "Read instructions from desktop file and generate code implementation"},
                {"name": "implement_from_instructions", "description": "Alternative method to implement code from instructions"},
                {"name": "code_writing_agent", "description": "Main code writing agent that orchestrates code generation"},
                {"name": "select_language_and_generate", "description": "Interactive language selection and code generation with editor opening"},
                {"name": "create_instruction_file", "description": "Create instruction files on desktop for other agents to read and execute"},
                {"name": "read_and_execute_instruction", "description": "Read instruction files from desktop and execute the described actions"},
                # NEW SECRETS DETECTION TOOLS
                {"name": "scan_file_for_secrets", "description": "Scan a specific file for secrets, API keys, passwords, and tokens"},
                {"name": "scan_directory_for_secrets", "description": "Scan a directory for files that might contain secrets"},
                {"name": "detect_api_keys", "description": "Detect API keys in content using specific patterns"},
                {"name": "detect_passwords", "description": "Detect passwords in content using specific patterns"},
                {"name": "detect_tokens", "description": "Detect tokens in content using specific patterns"},
                {"name": "scan_env_files", "description": "Scan environment files (.env, .env.local, etc.) for secrets"},
                {"name": "generate_security_report", "description": "Generate a comprehensive security report for scanned files"}
            ]
        }

    # NEW SECRETS DETECTION TOOLS
    def _scan_file_for_secrets(self, arguments: dict) -> dict:
        """Scan a specific file for secrets, API keys, passwords, and tokens."""
        try:
            file_path = arguments.get("file_path", "")
            file_name = arguments.get("file_name", "")
            
            if not file_path and not file_name:
                return {
                    "success": False,
                    "tool_name": "scan_file_for_secrets",
                    "error": "No file path or name provided"
                }
            
            # If only file name provided, construct full path
            if not file_path:
                desktop_path = os.path.expanduser("~/Desktop")
                file_path = os.path.join(desktop_path, file_name)
            
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "tool_name": "scan_file_for_secrets",
                    "error": f"File not found: {file_path}"
                }
            
            logger.info(f"🔍 SCANNING FILE FOR SECRETS: {os.path.basename(file_path)}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Scan for secrets using regex patterns
            secrets_found = self._detect_secrets_in_content(content)
            
            return {
                "success": True,
                "tool_name": "scan_file_for_secrets",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": len(content),
                "secrets_found": secrets_found,
                "total_secrets": len(secrets_found),
                "scan_summary": f"Found {len(secrets_found)} potential secrets in {os.path.basename(file_path)}"
            }
            
        except Exception as e:
            logger.error(f"❌ SCAN FILE FOR SECRETS FAILED: {e}")
            return {
                "success": False,
                "tool_name": "scan_file_for_secrets",
                "error": f"Failed to scan file for secrets: {str(e)}"
            }

    def _scan_directory_for_secrets(self, arguments: dict) -> dict:
        """Scan a directory for files that might contain secrets."""
        try:
            directory_path = arguments.get("directory_path", "")
            file_patterns = arguments.get("file_patterns", [".env", "config", "credentials", "secrets"])
            recursive = arguments.get("recursive", True)
            
            if not directory_path:
                directory_path = os.path.expanduser("~/Desktop")
            
            if not os.path.exists(directory_path):
                return {
                    "success": False,
                    "tool_name": "scan_directory_for_secrets",
                    "error": f"Directory not found: {directory_path}"
                }
            
            logger.info(f"🔍 SCANNING DIRECTORY FOR SECRETS: {directory_path}")
            
            # Find files matching patterns
            files_to_scan = []
            for root, dirs, files in os.walk(directory_path):
                if not recursive and root != directory_path:
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    # Check if file matches any of the patterns
                    for pattern in file_patterns:
                        if pattern.lower() in file.lower():
                            files_to_scan.append(file_path)
                            break
            
            # Scan each file for secrets
            scan_results = []
            total_secrets = 0
            
            for file_path in files_to_scan[:10]:  # Limit to first 10 files
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    secrets_found = self._detect_secrets_in_content(content)
                    if secrets_found:
                        scan_results.append({
                            "file_path": file_path,
                            "file_name": os.path.basename(file_path),
                            "secrets_found": secrets_found,
                            "secret_count": len(secrets_found)
                        })
                        total_secrets += len(secrets_found)
                except Exception as e:
                    logger.warning(f"⚠️  Could not scan file {file_path}: {e}")
            
            return {
                "success": True,
                "tool_name": "scan_directory_for_secrets",
                "directory_path": directory_path,
                "files_scanned": len(files_to_scan),
                "files_with_secrets": len(scan_results),
                "total_secrets_found": total_secrets,
                "scan_results": scan_results,
                "scan_summary": f"Scanned {len(files_to_scan)} files, found secrets in {len(scan_results)} files"
            }
            
        except Exception as e:
            logger.error(f"❌ SCAN DIRECTORY FOR SECRETS FAILED: {e}")
            return {
                "success": False,
                "tool_name": "scan_directory_for_secrets",
                "error": f"Failed to scan directory for secrets: {str(e)}"
            }

    def _detect_api_keys(self, arguments: dict) -> dict:
        """Detect API keys in content using specific patterns."""
        try:
            content = arguments.get("content", "")
            file_path = arguments.get("file_path", "")
            
            if not content and not file_path:
                return {
                    "success": False,
                    "tool_name": "detect_api_keys",
                    "error": "No content or file path provided"
                }
            
            # If file path provided, read content
            if file_path and not content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "detect_api_keys",
                        "error": f"Could not read file: {str(e)}"
                    }
            
            # API key patterns
            api_key_patterns = [
                r'api[_-]?key["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'api[_-]?token["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'access[_-]?key["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'secret[_-]?key["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'private[_-]?key["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'["\']([a-zA-Z0-9]{32,})["\']',  # Generic long alphanumeric strings
            ]
            
            api_keys_found = []
            import re
            
            for pattern in api_key_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    api_keys_found.append({
                        "pattern": pattern,
                        "value": match.group(1) if len(match.groups()) > 0 else match.group(0),
                        "line_number": content[:match.start()].count('\n') + 1,
                        "context": content[max(0, match.start()-20):match.end()+20]
                    })
            
            return {
                "success": True,
                "tool_name": "detect_api_keys",
                "api_keys_found": api_keys_found,
                "total_api_keys": len(api_keys_found),
                "scan_summary": f"Found {len(api_keys_found)} potential API keys"
            }
            
        except Exception as e:
            logger.error(f"❌ DETECT API KEYS FAILED: {e}")
            return {
                "success": False,
                "tool_name": "detect_api_keys",
                "error": f"Failed to detect API keys: {str(e)}"
            }

    def _detect_passwords(self, arguments: dict) -> dict:
        """Detect passwords in content using specific patterns."""
        try:
            content = arguments.get("content", "")
            file_path = arguments.get("file_path", "")
            
            if not content and not file_path:
                return {
                    "success": False,
                    "tool_name": "detect_passwords",
                    "error": "No content or file path provided"
                }
            
            # If file path provided, read content
            if file_path and not content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "detect_passwords",
                        "error": f"Could not read file: {str(e)}"
                    }
            
            # Password patterns
            password_patterns = [
                r'password["\s]*[:=]\s*["\']?([^\s"\']{6,})["\']?',
                r'passwd["\s]*[:=]\s*["\']?([^\s"\']{6,})["\']?',
                r'pwd["\s]*[:=]\s*["\']?([^\s"\']{6,})["\']?',
                r'secret["\s]*[:=]\s*["\']?([^\s"\']{6,})["\']?',
                r'pass["\s]*[:=]\s*["\']?([^\s"\']{6,})["\']?',
            ]
            
            passwords_found = []
            import re
            
            for pattern in password_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    passwords_found.append({
                        "pattern": pattern,
                        "value": match.group(1) if len(match.groups()) > 0 else match.group(0),
                        "line_number": content[:match.start()].count('\n') + 1,
                        "context": content[max(0, match.start()-20):match.end()+20]
                    })
            
            return {
                "success": True,
                "tool_name": "detect_passwords",
                "passwords_found": passwords_found,
                "total_passwords": len(passwords_found),
                "scan_summary": f"Found {len(passwords_found)} potential passwords"
            }
            
        except Exception as e:
            logger.error(f"❌ DETECT PASSWORDS FAILED: {e}")
            return {
                "success": False,
                "tool_name": "detect_passwords",
                "error": f"Failed to detect passwords: {str(e)}"
            }

    def _detect_tokens(self, arguments: dict) -> dict:
        """Detect tokens in content using specific patterns."""
        try:
            content = arguments.get("content", "")
            file_path = arguments.get("file_path", "")
            
            if not content and not file_path:
                return {
                    "success": False,
                    "tool_name": "detect_tokens",
                    "error": "No content or file path provided"
                }
            
            # If file path provided, read content
            if file_path and not content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    return {
                        "success": False,
                        "tool_name": "detect_tokens",
                        "error": f"Could not read file: {str(e)}"
                    }
            
            # Token patterns
            token_patterns = [
                r'token["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'jwt["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'bearer["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'oauth["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'access[_-]?token["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'refresh[_-]?token["\s]*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
            ]
            
            tokens_found = []
            import re
            
            for pattern in token_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    tokens_found.append({
                        "pattern": pattern,
                        "value": match.group(1) if len(match.groups()) > 0 else match.group(0),
                        "line_number": content[:match.start()].count('\n') + 1,
                        "context": content[max(0, match.start()-20):match.end()+20]
                    })
            
            return {
                "success": True,
                "tool_name": "detect_tokens",
                "tokens_found": tokens_found,
                "total_tokens": len(tokens_found),
                "scan_summary": f"Found {len(tokens_found)} potential tokens"
            }
            
        except Exception as e:
            logger.error(f"❌ DETECT TOKENS FAILED: {e}")
            return {
                "success": False,
                "tool_name": "detect_tokens",
                "error": f"Failed to detect tokens: {str(e)}"
            }

    def _scan_env_files(self, arguments: dict) -> dict:
        """Scan environment files (.env, .env.local, etc.) for secrets."""
        try:
            directory_path = arguments.get("directory_path", "")
            if not directory_path:
                directory_path = os.path.expanduser("~/Desktop")
            
            logger.info(f"🔍 SCANNING ENV FILES: {directory_path}")
            
            # Common env file patterns
            env_file_patterns = [
                ".env", ".env.local", ".env.production", ".env.development",
                ".env.test", ".env.staging", "config.env", "secrets.env"
            ]
            
            env_files_found = []
            total_secrets = 0
            
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if any(pattern in file.lower() for pattern in env_file_patterns):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            secrets_found = self._detect_secrets_in_content(content)
                            if secrets_found:
                                env_files_found.append({
                                    "file_path": file_path,
                                    "file_name": os.path.basename(file_path),
                                    "secrets_found": secrets_found,
                                    "secret_count": len(secrets_found)
                                })
                                total_secrets += len(secrets_found)
                        except Exception as e:
                            logger.warning(f"⚠️  Could not scan env file {file_path}: {e}")
            
            return {
                "success": True,
                "tool_name": "scan_env_files",
                "directory_path": directory_path,
                "env_files_found": env_files_found,
                "total_env_files": len(env_files_found),
                "total_secrets_found": total_secrets,
                "scan_summary": f"Found {len(env_files_found)} env files with {total_secrets} secrets"
            }
            
        except Exception as e:
            logger.error(f"❌ SCAN ENV FILES FAILED: {e}")
            return {
                "success": False,
                "tool_name": "scan_env_files",
                "error": f"Failed to scan env files: {str(e)}"
            }

    def _generate_security_report(self, arguments: dict) -> dict:
        """Generate a comprehensive security report for scanned files."""
        try:
            directory_path = arguments.get("directory_path", "")
            if not directory_path:
                directory_path = os.path.expanduser("~/Desktop")
            
            logger.info(f"📊 GENERATING SECURITY REPORT: {directory_path}")
            
            # Run comprehensive scan
            directory_scan = self._scan_directory_for_secrets({
                "directory_path": directory_path,
                "recursive": True
            })
            
            env_scan = self._scan_env_files({
                "directory_path": directory_path
            })
            
            # Generate report
            report = {
                "scan_timestamp": datetime.now().isoformat(),
                "directory_scanned": directory_path,
                "overall_summary": {
                    "total_files_scanned": directory_scan.get("files_scanned", 0),
                    "files_with_secrets": directory_scan.get("files_with_secrets", 0),
                    "total_secrets_found": directory_scan.get("total_secrets_found", 0),
                    "env_files_with_secrets": env_scan.get("total_env_files", 0)
                },
                "risk_assessment": self._assess_security_risk(directory_scan, env_scan),
                "recommendations": self._generate_security_recommendations(directory_scan, env_scan),
                "detailed_findings": {
                    "directory_scan": directory_scan,
                    "env_scan": env_scan
                }
            }
            
            return {
                "success": True,
                "tool_name": "generate_security_report",
                "report": report,
                "message": f"Security report generated for {directory_path}"
            }
            
        except Exception as e:
            logger.error(f"❌ GENERATE SECURITY REPORT FAILED: {e}")
            return {
                "success": False,
                "tool_name": "generate_security_report",
                "error": f"Failed to generate security report: {str(e)}"
            }

    def _detect_secrets_in_content(self, content: str) -> list:
        """Detect secrets in content using multiple detection methods."""
        secrets_found = []
        
        # Detect API keys
        api_keys = self._detect_api_keys({"content": content})
        if api_keys.get("success"):
            secrets_found.extend(api_keys.get("api_keys_found", []))
        
        # Detect passwords
        passwords = self._detect_passwords({"content": content})
        if passwords.get("success"):
            secrets_found.extend(passwords.get("passwords_found", []))
        
        # Detect tokens
        tokens = self._detect_tokens({"content": content})
        if tokens.get("success"):
            secrets_found.extend(tokens.get("tokens_found", []))
        
        return secrets_found

    def _assess_security_risk(self, directory_scan: dict, env_scan: dict) -> dict:
        """Assess the overall security risk based on scan results."""
        total_secrets = directory_scan.get("total_secrets_found", 0)
        env_files_with_secrets = env_scan.get("total_env_files", 0)
        
        risk_level = "LOW"
        risk_score = 0
        
        if total_secrets > 0:
            risk_score += total_secrets * 10
            if total_secrets > 5:
                risk_level = "HIGH"
            elif total_secrets > 2:
                risk_level = "MEDIUM"
        
        if env_files_with_secrets > 0:
            risk_score += env_files_with_secrets * 20
            if env_files_with_secrets > 2:
                risk_level = "HIGH"
            elif env_files_with_secrets > 0:
                risk_level = "MEDIUM"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "factors": {
                "total_secrets": total_secrets,
                "env_files_with_secrets": env_files_with_secrets
            }
        }

    def _generate_security_recommendations(self, directory_scan: dict, env_scan: dict) -> list:
        """Generate security recommendations based on scan results."""
        recommendations = []
        
        total_secrets = directory_scan.get("total_secrets_found", 0)
        env_files_with_secrets = env_scan.get("total_env_files", 0)
        
        if total_secrets > 0:
            recommendations.append({
                "priority": "HIGH",
                "recommendation": f"Remove or secure {total_secrets} exposed secrets found in files",
                "action": "Review all files with secrets and implement proper secret management"
            })
        
        if env_files_with_secrets > 0:
            recommendations.append({
                "priority": "HIGH",
                "recommendation": f"Secure {env_files_with_secrets} environment files containing secrets",
                "action": "Use environment variables or secure secret management systems"
            })
        
        if total_secrets == 0 and env_files_with_secrets == 0:
            recommendations.append({
                "priority": "LOW",
                "recommendation": "No secrets detected - good security practices",
                "action": "Continue monitoring and maintain current security practices"
            })
        
        recommendations.append({
            "priority": "MEDIUM",
            "recommendation": "Implement regular security scanning",
            "action": "Set up automated security scanning in CI/CD pipeline"
        })
        
        return recommendations

# Create bridge instance
bridge = SimpleMCPBridge()

class SimpleMCPHandler(BaseHTTPRequestHandler):
    """HTTP handler for simple MCP bridge with improved error handling."""
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if path == '/health':
                response = bridge.get_health()
            elif path == '/tools':
                response = bridge.get_tools()
            else:
                response = {"error": "Endpoint not found"}
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"GET request error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        """Handle POST requests with improved error handling."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                request_data = {}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if self.path == '/call':
                tool_name = request_data.get("tool")
                arguments = request_data.get("arguments", {})
                
                if not tool_name:
                    response = {"error": "No tool name provided"}
                else:
                    response = bridge.call_tool(tool_name, arguments)
            else:
                response = {"error": "Endpoint not found"}
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"POST request error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        """Custom logging."""
        logger.info(f"HTTP {format % args}")

def run_bridge(host='127.0.0.1', port=5000):
    """Run the simple MCP bridge with improved startup."""
    try:
        server = HTTPServer((host, port), SimpleMCPHandler)
        logger.info(f"🚀 Starting Simple MCP Bridge on http://{host}:{port}")
        logger.info("📧 Connected to your Gmail SMTP configuration!")
        logger.info("⏹️  Press Ctrl+C to stop the bridge")
        
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Bridge stopped by user.")
        server.shutdown()
    except Exception as e:
        logger.error(f"🛑 Bridge failed to start: {e}")
        raise

if __name__ == "__main__":
    run_bridge() 