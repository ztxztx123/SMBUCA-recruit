import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="处理协会招新报名表")
parser.add_argument("csv_file", help="输入 CSV 文件的路径")
args = parser.parse_args()

df = pd.read_csv(
    args.csv_file,
    dtype="string",
    keep_default_na=False,
    encoding="utf-8-sig",
    skip_blank_lines=False,
)

required_columns = ["姓名", "学号", "邮箱", "志愿1", "志愿2", "推荐人"]

missing_columns = set(required_columns) - set(df.columns)
if missing_columns:
    raise ValueError(f"缺少字段：{sorted(missing_columns)}")

df = df[required_columns]

print("总行数：", len(df))

# 空字符串和只有空白字符的字段，都算空值
empty_counts = df.apply(lambda column: column.str.strip().eq("")).sum()
print("每列空值数：")
print(empty_counts)

print("有没有完全重复的行：", df.duplicated().any())
print("多余的完全重复行数：", df.duplicated().sum())

raw = df.copy()
df = df.apply(lambda column: column.str.strip())

student_id = df["学号"]

bad_id = ~student_id.str.fullmatch(r"[0-9]+", na=False)

bad_email = df["邮箱"] != student_id + "@smbu.edu.cn"

duplicate_id = (
    student_id.ne("")
    & df.duplicated(subset=["学号"], keep=False)
)

reasons = pd.Series("", index=df.index, dtype="string")

checks = [
    (bad_id, "学号为空或不是纯数字；"),
    (bad_email, "邮箱与学号@smbu.edu.cn不一致；"),
    (duplicate_id, "同一学号重复报名；"),
]

for condition, message in checks:
    reasons.loc[condition] = reasons.loc[condition] + message

has_problem = reasons.ne("")

problems = raw.loc[has_problem].copy()
problems["数据记录序号"] = problems.index + 1
problems["问题原因"] = reasons.loc[has_problem]

problems.to_csv("problems.csv", index=False, encoding="utf-8-sig")

clean = df.loc[~has_problem].copy()