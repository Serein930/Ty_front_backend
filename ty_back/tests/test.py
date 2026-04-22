from topic_ast_engine import TopicRuleEngine

engine = TopicRuleEngine.from_json_file("your_rules.json")
result = engine.tag_message(your_message_dict)
print(result["topic_ids"])
print(result["topic_labels"])
print(result["matched_rules"])