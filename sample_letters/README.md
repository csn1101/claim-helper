# sample_letters

Thirteen **fictional** insurance letters for developing and testing the claim-helper extraction code.

All insurers, people, hospitals, claim numbers, policy numbers, phone numbers and email addresses are invented
(email addresses use the reserved `.example` domain). Any resemblance to real people or companies is accidental.
Each letter ends with a line saying it is a synthetic sample. Extraction code can ignore that line.

These letters are NOT real insurer templates, and the clause numbers are made up. Real letters vary a lot.
Never add a real person's letter to this folder or to the repo.

## Files

- `letter_01_...` to `letter_13_...`: the letters (plain text)
- `answer_key.json`: the expected extraction for each letter

## Answer key fields

| Field | Meaning |
|---|---|
| file | letter file name |
| insurer, claim_number, policy_number | as printed in the letter |
| policyholder_name, patient_name | may be different people |
| hospital | hospital name and city |
| letter_date, admission_date, discharge_date | ISO format (YYYY-MM-DD) |
| claim_amount_inr, approved_amount_inr, deduction_amount_inr | whole rupees as numbers. deduction = claim - approved |
| decision | rejected, partially_settled or closed_pending_documents |
| rejection_category | short label, see below |
| clause_cited | clause as written in the letter, or null if none is given |
| reason_summary | one-sentence summary |
| testing_notes | what this letter is designed to test |

Categories used: pre_existing_disease, initial_waiting_period, specific_waiting_period, non_disclosure,
room_rent_proportionate_deduction, non_payable_items, late_intimation, insufficient_documents,
policy_not_in_force, hospitalisation_under_24_hours, sub_limit_exceeded, excluded_treatment, unspecified.

## What the letters vary on purpose

- Date formats: 02/04/2026, 20 February 2026, 28th May 2026, 24.04.2026, 18-07-2026, 14-Aug-2026
- Amount formats: Rs. 2,45,000/-, INR 38,500, ₹72,000/-, Rs. 4,80,000
- Policyholder and patient being the same or different people
- Extra dates in the text that are not the letter, admission or discharge date
- Partial settlements with several amounts, and one letter with no clause cited (letter 13)
- One letter that is a closure for missing documents, not a rejection on the merits (letter 8)

## Not covered yet

Scanned or photographed letters (they need OCR first), Hindi and other Indian languages, letters with tables
as images, and insurer letters that mix several claims.
