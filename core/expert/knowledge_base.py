import os
import yaml

class Rule:
    def __init__(self, rule_dict: dict):
        self.id = rule_dict["id"]
        self.name = rule_dict["name"]
        self.severity = rule_dict["severity"]
        self.condition = rule_dict["condition"]
        self.consequence = rule_dict["consequence"]

    def __repr__(self):
        return f"Rule({self.id}: {self.name})"

class KnowledgeBase:
    def __init__(self, rules_dir: str):
        self.rules: list[Rule] = []
        self.load_rules_from_dir(rules_dir)

    def load_rules_from_dir(self, rules_dir: str):
        if not os.path.exists(rules_dir):
            raise FileNotFoundError(f"Rules directory not found: {rules_dir}")
            
        for file in os.listdir(rules_dir):
            if file.endswith(".yaml") or file.endswith(".yml"):
                file_path = os.path.join(rules_dir, file)
                with open(file_path, "r") as f:
                    try:
                        data = yaml.safe_load(f)
                        if data and "rules" in data:
                            for rule_data in data["rules"]:
                                self.rules.append(Rule(rule_data))
                    except yaml.YAMLError as exc:
                        print(f"Error loading YAML rule file {file_path}: {exc}")
                        
        print(f"Loaded {len(self.rules)} rules from knowledge base.")
