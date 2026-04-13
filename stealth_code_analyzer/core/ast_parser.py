import ast
import json
import os

class CodeParser:
    def __init__(self, language, rules_path='rules/rules.json'):
        self.language = language
        # Intentar cargar reglas desde ruta relativa o absoluta sugerida
        full_rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), rules_path)
        if not os.path.exists(full_rules_path):
             full_rules_path = rules_path # Fallback a ruta relativa de ejecución
             
        with open(full_rules_path, 'r') as f:
            self.rules = json.load(f)
        self.sources = self.rules.get('sources', {}).get(language, [])
        self.sinks = self.rules.get('sinks', {}).get(language, {})
        self.sanitizers = self.rules.get('sanitizers', {}).get(language, [])

    def parse_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if self.language == 'python':
                tree = ast.parse(content)
                return self._analyze_python(tree, file_path)
            return []
        except Exception as e:
            print(f"[-] Error parsing {file_path}: {e}")
            return []

    def _get_full_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val_name = self._get_full_name(node.value)
            if val_name:
                return f"{val_name}.{node.attr}"
            return node.attr
        return ""

    def _is_tainted(self, node, tainted_vars):
        if isinstance(node, ast.Name) and node.id in tainted_vars:
            return True
        if isinstance(node, ast.Call):
            full_name = self._get_full_name(node.func)
            if any(s in full_name for s in self.sources):
                return True
        return False

    def _analyze_python(self, tree, file_path):
        vulnerabilities = []
        tainted_vars = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if self._is_tainted(node.value, tainted_vars):
                            tainted_vars.add(target.id)
            
            if isinstance(node, ast.Call):
                full_name = self._get_full_name(node.func)
                if full_name:
                    # Comprobar si el nombre de la función (o su parte final) es un sink
                    for vuln_type, sinks in self.sinks.items():
                        if any(full_name.endswith(sink) or full_name == sink for sink in sinks):
                            for arg in node.args:
                                if self._is_tainted(arg, tainted_vars):
                                    vulnerabilities.append({
                                        "type": vuln_type,
                                        "file": file_path,
                                        "line": node.lineno,
                                        "sink": full_name,
                                        "details": f"Detección de Taint: Fuente insegura llega a '{full_name}'"
                                    })
                                    break
        return vulnerabilities
