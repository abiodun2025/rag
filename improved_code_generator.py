#!/usr/bin/env python3
"""
Improved Code Generator
Generates functional code based on specific requirements instead of just boilerplate.
"""

import re
import os
from typing import Dict, List, Any

class ImprovedCodeGenerator:
    def __init__(self):
        self.language_templates = {
            'kotlin': self._generate_kotlin_functional,
            'python': self._generate_python_functional,
            'javascript': self._generate_javascript_functional,
            'java': self._generate_java_functional,
            'go': self._generate_generic_functional,
            'rust': self._generate_generic_functional,
            'csharp': self._generate_generic_functional,
            'php': self._generate_generic_functional,
            'ruby': self._generate_generic_functional,
            'swift': self._generate_generic_functional
        }
    
    def generate_code(self, instructions: str, language: str, include_tests: bool = True, include_docs: bool = True) -> str:
        """Generate functional code based on instructions."""
        
        # Parse instructions to understand the actual requirements
        parsed = self._parse_instructions(instructions)
        
        # Get the appropriate generator
        generator = self.language_templates.get(language.lower(), self._generate_generic_functional)
        
        # Generate the code
        return generator(parsed, include_tests, include_docs)
    
    def _parse_instructions(self, instructions: str) -> Dict[str, Any]:
        """Parse instructions to extract specific requirements."""
        parsed = {
            'title': '',
            'function_name': '',
            'parameters': [],
            'return_type': '',
            'logic': '',
            'requirements': [],
            'features': [],
            'constraints': []
        }
        
        # Extract function name and parameters from common patterns
        function_patterns = [
            r'(?:me\s+a\s+)?(?:kotlin|python|java|javascript|typescript|go|rust|csharp|php|ruby|swift)\s+function\s+that\s+(?:add|subtract|multiply|divide|calculate|compute|find|get|create|generate|process|analyze)\s+(.+)',
            r'(?:create|write|generate)\s+(?:a\s+)?(?:function|method)\s+(?:that\s+)?(.+)',
            r'(?:add|subtract|multiply|divide|calculate|compute|find|get|create|generate|process|analyze)\s+(.+)',
            r'function\s+(?:to\s+)?(.+)',
            r'(.+)'  # Catch all pattern
        ]
        
        for pattern in function_patterns:
            match = re.search(pattern, instructions.lower())
            if match:
                parsed['function_name'] = self._extract_function_name(match.group(1))
                parsed['parameters'] = self._extract_parameters(match.group(1))
                parsed['return_type'] = self._extract_return_type(match.group(1))
                parsed['logic'] = self._extract_logic(match.group(1))
                break
        
        # Always check the entire instruction for logic to ensure we don't miss anything
        parsed['logic'] = self._extract_logic(instructions.lower())
        
        # Extract title
        if not parsed['title']:
            parsed['title'] = parsed['function_name'] or 'Generated Function'
        
        return parsed
    
    def _extract_function_name(self, description: str) -> str:
        """Extract function name from description."""
        # Look for specific patterns
        if 'add' in description.lower():
            return 'AddNumbers'
        elif 'subtract' in description.lower():
            return 'SubtractNumbers'
        elif 'multiply' in description.lower():
            return 'MultiplyNumbers'
        elif 'divide' in description.lower():
            return 'DivideNumbers'
        elif any(word in description.lower() for word in ['email', 'send', 'notification', 'mail']):
            return 'SendEmailNotification'
        else:
            # Extract meaningful words
            words = re.findall(r'\b\w+\b', description.lower())
            # Filter out common words and numbers
            filtered_words = [w for w in words if w not in ['a', 'an', 'the', 'that', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'] and not w.isdigit()]
            if filtered_words:
                return ''.join(word.capitalize() for word in filtered_words[:3])
        
        return 'AddNumbers'  # Default to AddNumbers for better function names
    
    def _extract_parameters(self, description: str) -> List[Dict[str, str]]:
        """Extract parameters from description."""
        parameters = []
        
        # Look for specific number patterns like "4 and 10"
        specific_patterns = [
            (r'(\d+)\s+and\s+(\d+)', 'Int'),  # "4 and 10"
            (r'(\d+)\s+(\d+)', 'Int'),        # "4 10"
            (r'(\d+)', 'Int'),                # individual numbers
        ]
        
        for pattern, param_type in specific_patterns:
            matches = re.findall(pattern, description)
            for i, match in enumerate(matches):
                if isinstance(match, tuple):
                    # Handle multiple numbers in one match
                    for j, value in enumerate(match):
                        parameters.append({
                            'name': f'num{j+1}',
                            'type': param_type,
                            'value': value
                        })
                else:
                    # Single number
                    parameters.append({
                        'name': f'num{i+1}',
                        'type': param_type,
                        'value': match
                    })
            
            # If we found specific numbers, use them
            if parameters:
                break
        
        # If no specific parameters found, create generic ones
        if not parameters:
            parameters = [
                {'name': 'a', 'type': 'Int', 'value': '0'},
                {'name': 'b', 'type': 'Int', 'value': '0'}
            ]
        
        return parameters
    
    def _extract_return_type(self, description: str) -> str:
        """Extract return type from description."""
        if any(word in description.lower() for word in ['add', 'subtract', 'multiply', 'divide', 'sum', 'total']):
            return 'Int'
        elif any(word in description.lower() for word in ['average', 'mean']):
            return 'Double'
        elif any(word in description.lower() for word in ['find', 'search', 'get']):
            return 'String'
        elif any(word in description.lower() for word in ['email', 'send', 'notification', 'mail']):
            return 'Boolean'
        else:
            return 'Int'  # Default to Int for numeric operations
    
    def _extract_logic(self, description: str) -> str:
        """Extract the actual logic to implement."""
        description_lower = description.lower()
        
        # Check for specific operation words
        if any(word in description_lower for word in ['add', 'addition', 'sum', 'plus']):
            return 'addition'
        elif any(word in description_lower for word in ['subtract', 'subtraction', 'minus', 'difference']):
            return 'subtraction'
        elif any(word in description_lower for word in ['multiply', 'multiplication', 'product', 'times']):
            return 'multiplication'
        elif any(word in description_lower for word in ['divide', 'division', 'quotient']):
            return 'division'
        elif any(word in description_lower for word in ['calculate', 'compute', 'evaluate']):
            return 'calculation'
        elif any(word in description_lower for word in ['find', 'search', 'locate']):
            return 'search'
        elif any(word in description_lower for word in ['get', 'retrieve', 'fetch']):
            return 'retrieval'
        elif any(word in description_lower for word in ['email', 'send', 'notification', 'mail']):
            return 'email_notification'
        else:
            return 'custom'
    
    def _generate_kotlin_functional(self, parsed: Dict[str, Any], include_tests: bool, include_docs: bool) -> str:
        """Generate functional Kotlin code."""
        
        function_name = parsed['function_name']
        parameters = parsed['parameters']
        return_type = parsed['return_type']
        logic = parsed['logic']
        
        code_parts = []
        
        # Add imports based on logic
        if logic == 'email_notification':
            code_parts.append("import java.util.Properties")
            code_parts.append("import javax.mail.*")
            code_parts.append("import javax.mail.internet.*")
            code_parts.append("")
        else:
            code_parts.append("import kotlin.math.*")
            code_parts.append("")
        
        # Add documentation
        if include_docs:
            code_parts.append("/**")
            code_parts.append(f" * {function_name}")
            code_parts.append(" *")
            for param in parameters:
                code_parts.append(f" * @param {param['name']} {param['type']} parameter")
            code_parts.append(f" * @return {return_type} result")
            code_parts.append(" */")
        
        # Generate the actual function
        param_list = ", ".join([f"{param['name']}: {param['type']}" for param in parameters])
        
        code_parts.append(f"fun {function_name}({param_list}): {return_type} {{")
        
        # Add the actual implementation based on logic
        if logic == 'addition':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} + {parameters[1]['name']}")
            else:
                code_parts.append(f"    return {parameters[0]['name']}")
        elif logic == 'subtraction':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} - {parameters[1]['name']}")
            else:
                code_parts.append(f"    return -{parameters[0]['name']}")
        elif logic == 'multiplication':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} * {parameters[1]['name']}")
            else:
                code_parts.append(f"    return {parameters[0]['name']}")
        elif logic == 'division':
            if len(parameters) >= 2:
                code_parts.append(f"    return if ({parameters[1]['name']} != 0) {parameters[0]['name']} / {parameters[1]['name']} else 0")
            else:
                code_parts.append(f"    return {parameters[0]['name']}")
        elif logic == 'email_notification':
            code_parts.append("    val props = Properties()")
            code_parts.append("    props.put(\"mail.smtp.auth\", \"true\")")
            code_parts.append("    props.put(\"mail.smtp.starttls.enable\", \"true\")")
            code_parts.append("    props.put(\"mail.smtp.host\", \"smtp.gmail.com\")")
            code_parts.append("    props.put(\"mail.smtp.port\", \"587\")")
            code_parts.append("")
            code_parts.append("    val session = Session.getInstance(props, object : Authenticator() {")
            code_parts.append("        override fun getPasswordAuthentication(): PasswordAuthentication {")
            code_parts.append("            return PasswordAuthentication(\"your-email@gmail.com\", \"your-app-password\")")
            code_parts.append("        }")
            code_parts.append("    })")
            code_parts.append("")
            code_parts.append("    try {")
            code_parts.append("        val message = MimeMessage(session)")
            code_parts.append("        message.setFrom(InternetAddress(\"your-email@gmail.com\"))")
            code_parts.append("        message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(\"recipient@example.com\"))")
            code_parts.append("        message.subject = \"Notification\"")
            code_parts.append("        message.setText(\"This is a notification email.\")")
            code_parts.append("")
            code_parts.append("        Transport.send(message)")
            code_parts.append("        println(\"Email notification sent successfully!\")")
            code_parts.append("        return true")
            code_parts.append("    } catch (e: MessagingException) {")
            code_parts.append("        println(\"Failed to send email: ${e.message}\")")
            code_parts.append("        return false")
            code_parts.append("    }")
        else:
            # Generic implementation
            code_parts.append(f"    // TODO: Implement {logic} logic")
            code_parts.append(f"    return {parameters[0]['name']}")
        
        code_parts.append("}")
        code_parts.append("")
        
        # Add main function for testing
        code_parts.append("fun main() {")
        code_parts.append(f"    val result = {function_name}(")
        param_values = ", ".join([param['value'] for param in parameters])
        code_parts.append(f"        {param_values}")
        code_parts.append("    )")
        code_parts.append(f"    println(\"Result: $result\")")
        code_parts.append("}")
        
        # Add tests if requested
        if include_tests:
            code_parts.append("")
            code_parts.append("// Tests")
            code_parts.append(f"fun test{function_name}() {{")
            # Calculate expected result based on logic
            if logic == 'addition' and len(parameters) >= 2:
                expected = int(parameters[0]['value']) + int(parameters[1]['value'])
                code_parts.append(f"    val expected = {expected}")
                code_parts.append(f"    val result = {function_name}({', '.join([param['value'] for param in parameters])})")
                code_parts.append(f"    assert(result == expected) {{ \"Expected $expected but got $result\" }}")
            elif logic == 'subtraction' and len(parameters) >= 2:
                expected = int(parameters[0]['value']) - int(parameters[1]['value'])
                code_parts.append(f"    val expected = {expected}")
                code_parts.append(f"    val result = {function_name}({', '.join([param['value'] for param in parameters])})")
                code_parts.append(f"    assert(result == expected) {{ \"Expected $expected but got $result\" }}")
            elif logic == 'multiplication' and len(parameters) >= 2:
                expected = int(parameters[0]['value']) * int(parameters[1]['value'])
                code_parts.append(f"    val expected = {expected}")
                code_parts.append(f"    val result = {function_name}({', '.join([param['value'] for param in parameters])})")
                code_parts.append(f"    assert(result == expected) {{ \"Expected $expected but got $result\" }}")
            elif logic == 'division' and len(parameters) >= 2:
                expected = int(parameters[0]['value']) // int(parameters[1]['value'])
                code_parts.append(f"    val expected = {expected}")
                code_parts.append(f"    val result = {function_name}({', '.join([param['value'] for param in parameters])})")
                code_parts.append(f"    assert(result == expected) {{ \"Expected $expected but got $result\" }}")
            else:
                code_parts.append(f"    val result = {function_name}({', '.join([param['value'] for param in parameters])})")
                code_parts.append(f"    println(\"Test result: $result\")")
                code_parts.append(f"    assert(result != null)")
            code_parts.append("}")
        
        return "\n".join(code_parts)
    
    def _generate_python_functional(self, parsed: Dict[str, Any], include_tests: bool, include_docs: bool) -> str:
        """Generate functional Python code."""
        
        function_name = parsed['function_name']
        parameters = parsed['parameters']
        return_type = parsed['return_type']
        logic = parsed['logic']
        
        code_parts = []
        
        # Add shebang and docstring
        code_parts.append("#!/usr/bin/env python3")
        code_parts.append('"""')
        code_parts.append(f"{function_name} function")
        code_parts.append('"""')
        code_parts.append("")
        
        # Add type hints import
        code_parts.append("from typing import Union, Optional")
        code_parts.append("")
        
        # Generate the actual function
        param_list = ", ".join([param['name'] for param in parameters])
        type_hints = ", ".join([f"{param['name']}: {param['type']}" for param in parameters])
        
        if include_docs:
            code_parts.append(f"def {function_name}({type_hints}) -> {return_type}:")
            code_parts.append(f'    """')
            code_parts.append(f'    {function_name} function')
            code_parts.append(f'    ')
            for param in parameters:
                code_parts.append(f'    Args:')
                code_parts.append(f'        {param["name"]} ({param["type"]}): {param["name"]} parameter')
            code_parts.append(f'    ')
            code_parts.append(f'    Returns:')
            code_parts.append(f'        {return_type}: result')
            code_parts.append(f'    """')
        else:
            code_parts.append(f"def {function_name}({param_list}):")
        
        # Add the actual implementation
        if logic == 'addition':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} + {parameters[1]['name']}")
            else:
                code_parts.append(f"    return {parameters[0]['name']}")
        elif logic == 'subtraction':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} - {parameters[1]['name']}")
            else:
                code_parts.append(f"    return -{parameters[0]['name']}")
        elif logic == 'multiplication':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} * {parameters[1]['name']}")
            else:
                code_parts.append(f"    return {parameters[0]['name']}")
        elif logic == 'division':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} / {parameters[1]['name']} if {parameters[1]['name']} != 0 else 0")
            else:
                code_parts.append(f"    return {parameters[0]['name']}")
        else:
            code_parts.append(f"    # TODO: Implement {logic} logic")
            code_parts.append(f"    return {parameters[0]['name']}")
        
        code_parts.append("")
        
        # Add main execution
        code_parts.append("if __name__ == '__main__':")
        param_values = ", ".join([param['value'] for param in parameters])
        code_parts.append(f"    result = {function_name}({param_values})")
        code_parts.append(f'    print(f"Result: {{result}}")')
        
        # Add tests if requested
        if include_tests:
            code_parts.append("")
            code_parts.append("# Tests")
            code_parts.append("def test_${function_name}():")
            code_parts.append(f"    result = {function_name}(")
            test_values = ", ".join([param['value'] for param in parameters])
            code_parts.append(f"        {test_values}")
            code_parts.append("    )")
            code_parts.append(f'    print(f"Test result: {{result}}")')
            code_parts.append("    assert result is not None")
        
        return "\n".join(code_parts)
    
    def _generate_javascript_functional(self, parsed: Dict[str, Any], include_tests: bool, include_docs: bool) -> str:
        """Generate functional JavaScript code."""
        
        function_name = parsed['function_name']
        parameters = parsed['parameters']
        logic = parsed['logic']
        
        code_parts = []
        
        # Add JSDoc documentation
        if include_docs:
            code_parts.append("/**")
            code_parts.append(f" * {function_name}")
            code_parts.append(" *")
            for param in parameters:
                code_parts.append(f" * @param {{{param['type']}}} {param['name']} - {param['name']} parameter")
            code_parts.append(f" * @returns {{{parsed['return_type']}}} result")
            code_parts.append(" */")
        
        # Generate the actual function
        param_list = ", ".join([param['name'] for param in parameters])
        
        code_parts.append(f"function {function_name}({param_list}) {{")
        
        # Add the actual implementation
        if logic == 'addition':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} + {parameters[1]['name']};")
            else:
                code_parts.append(f"    return {parameters[0]['name']};")
        elif logic == 'subtraction':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} - {parameters[1]['name']};")
            else:
                code_parts.append(f"    return -{parameters[0]['name']};")
        elif logic == 'multiplication':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[0]['name']} * {parameters[1]['name']};")
            else:
                code_parts.append(f"    return {parameters[0]['name']};")
        elif logic == 'division':
            if len(parameters) >= 2:
                code_parts.append(f"    return {parameters[1]['name']} !== 0 ? {parameters[0]['name']} / {parameters[1]['name']} : 0;")
            else:
                code_parts.append(f"    return {parameters[0]['name']};")
        else:
            code_parts.append(f"    // TODO: Implement {logic} logic")
            code_parts.append(f"    return {parameters[0]['name']};")
        
        code_parts.append("}")
        code_parts.append("")
        
        # Add main execution
        param_values = ", ".join([param['value'] for param in parameters])
        code_parts.append(f"const result = {function_name}({param_values});")
        code_parts.append('console.log(`Result: ${result}`);')
        
        # Add tests if requested
        if include_tests:
            code_parts.append("")
            code_parts.append("// Tests")
            code_parts.append("function test${function_name}() {")
            code_parts.append(f"    const result = {function_name}(")
            test_values = ", ".join([param['value'] for param in parameters])
            code_parts.append(f"        {test_values}")
            code_parts.append("    );")
            code_parts.append('    console.log(`Test result: ${result}`);')
            code_parts.append("    console.assert(result !== null);")
            code_parts.append("}")
        
        return "\n".join(code_parts)
    
    def _generate_java_functional(self, parsed: Dict[str, Any], include_tests: bool, include_docs: bool) -> str:
        """Generate functional Java code."""
        
        function_name = parsed['function_name']
        parameters = parsed['parameters']
        return_type = parsed['return_type']
        logic = parsed['logic']
        
        code_parts = []
        
        # Add package and imports
        code_parts.append("package com.example;")
        code_parts.append("")
        code_parts.append("import java.util.*;")
        code_parts.append("")
        
        # Add class and documentation
        if include_docs:
            code_parts.append("/**")
            code_parts.append(f" * {function_name} class")
            code_parts.append(" */")
        
        code_parts.append("public class ${function_name} {")
        code_parts.append("")
        
        # Generate the actual method
        param_list = ", ".join([f"{param['type']} {param['name']}" for param in parameters])
        
        if include_docs:
            code_parts.append("    /**")
            code_parts.append(f"     * {function_name} method")
            code_parts.append("     *")
            for param in parameters:
                code_parts.append(f"     * @param {param['name']} {param['type']} parameter")
            code_parts.append(f"     * @return {return_type} result")
            code_parts.append("     */")
        
        code_parts.append(f"    public static {return_type} {function_name}({param_list}) {{")
        
        # Add the actual implementation
        if logic == 'addition':
            if len(parameters) >= 2:
                code_parts.append(f"        return {parameters[0]['name']} + {parameters[1]['name']};")
            else:
                code_parts.append(f"        return {parameters[0]['name']};")
        elif logic == 'subtraction':
            if len(parameters) >= 2:
                code_parts.append(f"        return {parameters[0]['name']} - {parameters[1]['name']};")
            else:
                code_parts.append(f"        return -{parameters[0]['name']};")
        elif logic == 'multiplication':
            if len(parameters) >= 2:
                code_parts.append(f"        return {parameters[0]['name']} * {parameters[1]['name']};")
            else:
                code_parts.append(f"        return {parameters[0]['name']};")
        elif logic == 'division':
            if len(parameters) >= 2:
                code_parts.append(f"        return {parameters[1]['name']} != 0 ? {parameters[0]['name']} / {parameters[1]['name']} : 0;")
            else:
                code_parts.append(f"        return {parameters[0]['name']};")
        else:
            code_parts.append(f"        // TODO: Implement {logic} logic")
            code_parts.append(f"        return {parameters[0]['name']};")
        
        code_parts.append("    }")
        code_parts.append("")
        
        # Add main method
        code_parts.append("    public static void main(String[] args) {")
        param_values = ", ".join([param['value'] for param in parameters])
        code_parts.append(f"        {return_type} result = {function_name}({param_values});")
        code_parts.append(f'        System.out.println("Result: " + result);')
        code_parts.append("    }")
        code_parts.append("}")
        
        return "\n".join(code_parts)
    
    def _generate_generic_functional(self, parsed: Dict[str, Any], include_tests: bool, include_docs: bool) -> str:
        """Generate generic functional code for unsupported languages."""
        
        function_name = parsed['function_name']
        parameters = parsed['parameters']
        logic = parsed['logic']
        
        code_parts = []
        
        code_parts.append(f"// {function_name} function")
        code_parts.append(f"// Language: Generic")
        code_parts.append("")
        
        # Add documentation
        if include_docs:
            code_parts.append("/*")
            code_parts.append(f" * {function_name}")
            code_parts.append(" *")
            for param in parameters:
                code_parts.append(f" * @param {param['name']} {param['type']} parameter")
            code_parts.append(" */")
        
        # Generate function signature
        param_list = ", ".join([f"{param['name']}: {param['type']}" for param in parameters])
        code_parts.append(f"function {function_name}({param_list}) {{")
        
        # Add implementation
        if logic == 'addition' and len(parameters) >= 2:
            code_parts.append(f"    return {parameters[0]['name']} + {parameters[1]['name']};")
        elif logic == 'subtraction' and len(parameters) >= 2:
            code_parts.append(f"    return {parameters[0]['name']} - {parameters[1]['name']};")
        elif logic == 'multiplication' and len(parameters) >= 2:
            code_parts.append(f"    return {parameters[0]['name']} * {parameters[1]['name']};")
        elif logic == 'division' and len(parameters) >= 2:
            code_parts.append(f"    return {parameters[0]['name']} / {parameters[1]['name']};")
        else:
            code_parts.append(f"    // TODO: Implement {logic} logic")
            code_parts.append(f"    return {parameters[0]['name']};")
        
        code_parts.append("}")
        
        return "\n".join(code_parts)

# Example usage
if __name__ == "__main__":
    generator = ImprovedCodeGenerator()
    
    # Test with your specific request
    instructions = "me a kotlin function that add two numbers 4 and 10"
    
    print("=== Generated Kotlin Code ===")
    kotlin_code = generator.generate_code(instructions, "kotlin", include_tests=True, include_docs=True)
    print(kotlin_code)
    
    print("\n=== Generated Python Code ===")
    python_code = generator.generate_code(instructions, "python", include_tests=True, include_docs=True)
    print(python_code) 