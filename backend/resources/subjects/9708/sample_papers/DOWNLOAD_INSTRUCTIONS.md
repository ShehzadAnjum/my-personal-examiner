# Economics 9708 Sample Papers - Download Instructions

**Purpose**: Download 10+ Economics past papers for testing PDF extraction accuracy

**Required**: Papers 2 & 3 (Data Response and Essays) from 2018-2023

---

## Cambridge International Past Papers

### Official Source

**Website**: https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-economics-9708/

**Past Papers Section**: Navigate to "Past papers and mark schemes" under the Economics 9708 qualification page

---

## Required Downloads (Minimum 10 Papers)

Download **both question papers (qp) and mark schemes (ms)** for each:

### Paper 2 (Data Response) - Minimum 3 Papers

1. **9708_s22_qp_22.pdf** - Summer 2022, Paper 2, Variant 2
2. **9708_s22_ms_22.pdf** - Summer 2022, Mark Scheme
3. **9708_w21_qp_23.pdf** - Winter 2021, Paper 2, Variant 3
4. **9708_w21_ms_23.pdf** - Winter 2021, Mark Scheme
5. **9708_s20_qp_21.pdf** - Summer 2020, Paper 2, Variant 1
6. **9708_s20_ms_21.pdf** - Summer 2020, Mark Scheme

### Paper 3 (Essays) - Minimum 5 Papers

1. **9708_s22_qp_31.pdf** - Summer 2022, Paper 3, Variant 1
2. **9708_s22_ms_31.pdf** - Summer 2022, Mark Scheme
3. **9708_w21_qp_32.pdf** - Winter 2021, Paper 3, Variant 2
4. **9708_w21_ms_32.pdf** - Winter 2021, Mark Scheme
5. **9708_s20_qp_33.pdf** - Summer 2020, Paper 3, Variant 3
6. **9708_s20_ms_33.pdf** - Summer 2020, Mark Scheme
7. **9708_w19_qp_31.pdf** - Winter 2019, Paper 3
8. **9708_w19_ms_31.pdf** - Winter 2019, Mark Scheme
9. **9708_s18_qp_32.pdf** - Summer 2018, Paper 3
10. **9708_s18_ms_32.pdf** - Summer 2018, Mark Scheme

---

## Filename Format Explanation

Cambridge International uses standard naming:

```
{subject_code}_{session}{year}_{paper_type}_{paper_number}.pdf
```

**Components**:
- **9708** - Economics subject code
- **s/m/w** - Session code (s=Summer May/June, m=March, w=Winter Oct/Nov)
- **22/21/20/19/18** - Year (last 2 digits: 2022, 2021, 2020, etc.)
- **qp/ms** - Paper type (qp=Question Paper, ms=Mark Scheme)
- **21/22/23/31/32/33** - Paper number and variant

**Examples**:
- `9708_s22_qp_31.pdf` → Economics, Summer 2022, Question Paper, Paper 3 Variant 1
- `9708_w21_ms_23.pdf` → Economics, Winter 2021, Mark Scheme, Paper 2 Variant 3

---

## Download Process

### Option 1: Cambridge Teacher Support (Recommended)

1. Create free teacher account at https://teachers.cambridgeinternational.org/
2. Navigate to Economics 9708
3. Download past papers from "Past papers" section
4. Place downloaded PDFs in this directory (`backend/resources/subjects/9708/sample_papers/`)

### Option 2: Alternative Sources (If No Teacher Access)

**Note**: Always prefer official Cambridge sources when possible

- **PapaCambridge**: https://www.papacambridge.com/ (Community-shared past papers)
- **GCE Guide**: https://www.gceguide.com/ (Unofficial archive)
- **Save My Exams**: https://www.savemyexams.com/ (Some free resources)

### Option 3: Manual Collection

If you already have Economics 9708 past papers from previous study:
- Scan or locate digital copies
- Rename to match Cambridge format if needed
- Ensure PDFs are text-based (not scanned images) for extraction to work

---

## Verification

After downloading, verify you have:

- [ ] At least 10 PDF files in this directory
- [ ] Mix of question papers (qp) and mark schemes (ms)
- [ ] Mix of Papers 2 and 3 (data response and essays)
- [ ] Filenames match Cambridge format: `9708_sYY_qp_NN.pdf`
- [ ] PDFs are text-based (not scanned images - test by selecting text in PDF viewer)

**Check**: Run this command from repository root:
```bash
ls -1 backend/resources/subjects/9708/sample_papers/*.pdf | wc -l
```

Expected output: **10 or more**

---

## Testing Extraction

Once PDFs are downloaded, test extraction accuracy:

```bash
# From repository root
cd backend

# Run extraction test
uv run python -m pytest tests/integration/test_economics_extraction.py -v

# Expected: >95% questions extracted correctly
```

---

## Troubleshooting

### PDF is Scanned Image (No Text Selection)

**Problem**: PDF is scanned image, not text-based
**Solution**: Use OCR tool (Tesseract) or find text-based version from Cambridge official source

### Filename Doesn't Match Format

**Problem**: Downloaded PDF named `Economics_Paper3_2022.pdf`
**Solution**: Rename to Cambridge format: `9708_s22_qp_31.pdf`

### Can't Access Cambridge Website

**Problem**: Teacher support requires school email
**Solution**: Use alternative sources (PapaCambridge, GCE Guide) as temporary measure, replace with official PDFs when possible

---

## Why These Specific Papers?

**Years 2018-2022**:
- Recent enough to match current syllabus format (2016-2023 syllabus)
- Old enough to be freely available (Cambridge releases past papers after 2 years)

**Papers 2 & 3 (Not Paper 1)**:
- Paper 1 is MCQ (requires OCR for diagrams) - deferred to later phase
- Papers 2 & 3 have text-based questions ideal for extraction testing
- Mix of short answers (Paper 2) and essays (Paper 3) tests robustness

**Multiple Variants (21, 22, 23, 31, 32, 33)**:
- Cambridge creates multiple variants for different time zones
- Testing multiple variants ensures extraction patterns handle all formats
- Variants have identical structure but different content

---

## After Download Complete

Once you have 10+ Economics PDFs:

1. ✅ Update `backend/resources/subjects/9708/extraction_patterns.yaml` based on actual PDF analysis
2. ✅ Update `backend/resources/subjects/9708/marking_config.json` with level descriptors from mark schemes
3. ✅ Run extraction tests: `uv run pytest tests/integration/test_economics_extraction.py`
4. ✅ Validate >95% extraction accuracy (Phase II Success Criterion SC-002)

---

**Status**: This directory should contain 10+ Economics past papers before proceeding with Phase 2 (Foundational) tasks.

**Next Task**: T005 (Phase 2) - Create database migration
