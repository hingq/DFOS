# Output

## 目录结构

```
data/output/product-profiles/
└── {slug}/
    ├── {slug}.yaml      # 结构化 Profile
    ├── {slug}.md        # 可读报告
    └── sources.md       # 来源与日期
```

`slug` 建议：小写字母、数字、连字符，如 `claude-design`、`figma-ai`。

## 命名与日期

- 文件内 `last_researched` 使用调研完成日  
- 若同日更新，可追加 `sources.md` 条目而非覆盖全部事实（团队约定为准）

## 验收检查

- [ ] YAML 可被解析  
- [ ] `sources.md` 至少包含官网与一条独立信源（若可获取）  
- [ ] 无「据传」「据说」类无来源断言
