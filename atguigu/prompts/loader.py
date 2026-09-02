from pathlib import Path


def load_prompt_template(prompt_template_name: str) -> str:
    """"
    通过提示词文件的名称读取提示词
    """
    prompt_path = Path(__file__).resolve().parents[0] / "jinja2" / f"{prompt_template_name}.jinja2"
    return prompt_path.read_text(encoding="utf-8")


if __name__ == '__main__':
    print(load_prompt_template("turn_plan"))
