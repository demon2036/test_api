import json
import csv
import glob
import os

def get_question_type(test):
    if test.get("filter"):
        return "advanced"
    if test.get("query_category") and test.get("query_category") not in ["basic_enumeration", "base_enumeration"]:
        return "advanced"
    if test.get("category") and test.get("category") == "高级功能":
        return "advanced"
    return "normal"

def main():
    json_files = glob.glob('enumerate_framework/output/**/*.json', recursive=True)
    
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['question', 'answers', 'source_file', 'question_type']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for file_path in json_files:
            file_name = os.path.basename(file_path)
            if file_name in ["homebrew.json", "cran.json", "go_proxy.json", "nuget.json"]:
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if "tests" in data:
                        for test_section in data["tests"]:
                            all_tests = []
                            # Case 1: dblp.json structure with base_test and enhanced_tests
                            if "base_test" in test_section or "enhanced_tests" in test_section:
                                if "base_test" in test_section:
                                    all_tests.append(test_section["base_test"])
                                if "enhanced_tests" in test_section:
                                    all_tests.extend(test_section["enhanced_tests"])
                            # Case 2: Nested tests structure (npm, pypi, crates, etc.)
                            elif "tests" in test_section and isinstance(test_section["tests"], list):
                                all_tests.extend(test_section["tests"])
                            # Case 3: Other files where the section is the test itself
                            else:
                                all_tests.append(test_section)

                            for test in all_tests:
                                question = test.get("question")
                                answers_raw = test.get("answers")
                                question_type = get_question_type(test)

                                if not question or answers_raw is None:
                                    if test.get("base_test"):
                                        question = test["base_test"].get("question")
                                        answers_raw = test["base_test"].get("answers")
                                        question_type = "normal" # base_test is always normal

                                if not question or answers_raw is None:
                                    continue

                                answer_list = []
                                if isinstance(answers_raw, list):
                                    for ans in answers_raw:
                                        if isinstance(ans, dict):
                                            answer_list.append(str(ans.get("answer")))
                                        else:
                                            answer_list.append(str(ans))
                                
                                writer.writerow({
                                    'question': question,
                                    'answers': '\n'.join(answer_list),
                                    'source_file': file_name,
                                    'question_type': question_type
                                })

                except json.JSONDecodeError:
                    print(f"Could not decode JSON from {file_path}")
                except Exception as e:
                    print(f"An error occurred while processing {file_path}: {e}")

if __name__ == '__main__':
    main()
