# Learning Resources

Central repository for all learning materials organized by qualification level and subject.

## Directory Structure

```
resources/
├── cambridge-a-level/          # Cambridge International A-Level (Age 16-19)
│   └── economics-9708/         # Economics (Subject Code: 9708)
│       ├── syllabus/           # Official syllabus documents
│       ├── textbooks/          # Recommended textbooks
│       ├── past-papers/        # Past examination papers (QP)
│       ├── mark-schemes/       # Mark schemes (MS)
│       ├── additional-materials/ # Notes, summaries, guides
│       ├── online-resources/   # Links to online content
│       ├── media/              # Videos, diagrams, animations
│       └── user-uploads/       # Student uploads for THIS subject
│           └── [student-id]/   # Per-student isolation
│
├── cambridge-o-level/          # Cambridge O-Level (Age 14-16)
│   └── [subject-code]/         # Subjects to be added
│
├── igcse/                      # Cambridge IGCSE (Age 14-16)
│   └── [subject-code]/         # Subjects to be added
│
└── matric/                     # Pakistan Matriculation
    └── [subject]/              # Subjects to be added
```

## Supported Qualifications

### Cambridge International
| Level | Typical Age | Code Format | Example |
|-------|-------------|-------------|---------|
| A-Level | 16-19 | 4 digits | 9708 (Economics) |
| AS-Level | 16-17 | 4 digits | 9708 (Economics) |
| O-Level | 14-16 | 4 digits | 2281 (Economics) |
| IGCSE | 14-16 | 4 digits | 0455 (Economics) |

### Pakistan Boards
| Level | Typical Age | Format |
|-------|-------------|--------|
| Matric | 14-16 | Subject name |
| Intermediate | 16-18 | Subject name |

## File Naming Conventions

### Past Papers
Format: `{code}_{session}{year}_{type}_{variant}.pdf`

Examples:
- `9708_s22_qp_31.pdf` - Summer 2022, Question Paper, Variant 31
- `9708_w21_ms_22.pdf` - Winter 2021, Mark Scheme, Variant 22

Session codes:
- `s` = Summer (May/June)
- `w` = Winter (Oct/Nov)
- `m` = March

Type codes:
- `qp` = Question Paper
- `ms` = Mark Scheme
- `er` = Examiner Report
- `gt` = Grade Thresholds

### Textbooks
Use publisher's full title with edition:
- `Cambridge-International-As-A-Level-Economics-Coursebook-4th-Edition.pdf`

## Adding New Subjects

1. Create directory: `{qualification}/{subject-code}/`
2. Create subdirectories: syllabus, textbooks, past-papers, mark-schemes, etc.
3. Add README.md with subject-specific information
4. Update this README with new subject

## Multi-Tenant Isolation

User-uploaded content is stored within each subject at `{subject}/user-uploads/{student-id}/`:

```
resources/cambridge-a-level/economics-9708/user-uploads/
├── student-abc123/           # Student A's Economics resources
│   ├── my-notes.pdf
│   └── practice-questions.pdf
└── student-xyz789/           # Student B's Economics resources
    └── revision-guide.pdf
```

Benefits:
- Data isolation between students
- Resources stay with their subject context
- Easy backup/restore per user per subject
- Compliance with privacy requirements
- Enables subject-specific resource recommendations

## Current Subjects

### Cambridge A-Level
- **Economics 9708** - Active (Phase I complete)

### Planned Additions
- Accounting 9706
- English General Paper 8021
- Mathematics 9709

---

**Last Updated**: 2026-01-05
**Maintained By**: My Personal Examiner Project
