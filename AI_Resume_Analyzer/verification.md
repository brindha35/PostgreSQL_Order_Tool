
# Resume Extraction - Manual Verification

## Prompt Details

- Prompt Version: v1.0
- Model: llama3.2:1b
- Temperature: 0
- Output Format: JSON

## Manual Verification

| Resume | Fields Checked | Errors |
|---|---|---|
| resume_01 | All 7 fields | 4 |
| resume_02 | All 7 fields | 4 |
| resume_03 | All 7 fields | 4 |

## Error Count

- Total resumes processed: 8
- Total resumes manually checked: 3
- Total extraction errors: 12

## Verification Notes

1. Candidate names matched original resumes.
2. Skills matched original resumes.
3. Experience matched original resumes.
4. Education matched original resumes.
5. Unsupported strengths were identified.
6. Skill evidence sentences were checked against original resumes.
7. Evidence hallucinations were counted as extraction errors.
