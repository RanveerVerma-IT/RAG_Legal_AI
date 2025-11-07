import re
from datetime import datetime
from typing import Dict, Any

from dateutil import parser as date_parser


NAME_RE = re.compile(r"(?:name is|name:|for)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)", re.IGNORECASE)
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"\b(?:\+91[-\s]?)?[6-9][0-9]{9}\b")
DOB_RE = re.compile(r"(?:dob|date of birth|born on)\s*[:\-]?\s*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})", re.IGNORECASE)


def parse_initial_entities(text: str) -> Dict[str, Any]:
	entities: Dict[str, Any] = {}
	name_match = NAME_RE.search(text)
	if name_match:
		entities["applicant_name"] = name_match.group(1).strip()
	mail_match = EMAIL_RE.search(text)
	if mail_match:
		entities["email"] = mail_match.group(0)
		entities["contact_email"] = mail_match.group(0)
	phone_match = PHONE_RE.search(text)
	if phone_match:
		entities["phone"] = phone_match.group(0)
		entities["contact_phone"] = phone_match.group(0)
	dob_match = DOB_RE.search(text)
	if dob_match:
		try:
			parsed = date_parser.parse(dob_match.group(1), dayfirst=True, fuzzy=True)
			dob_str = parsed.strftime("%d-%m-%Y")
			entities["date_of_birth"] = dob_str
			entities["groom_date_of_birth"] = dob_str
			entities["bride_date_of_birth"] = dob_str
		except Exception:
			pass
	# naive address extraction (prototype): look for 'address is:' or 'address:'
	addr = None
	for key in ["address is", "address:", "address-"]:
		idx = text.lower().find(key)
		if idx != -1:
			addr = text[idx + len(key):].strip()
			break
	if addr:
		# clip long free text
		entities["address"] = addr[:300].strip()
	
	# Marriage-specific entity extraction
	text_lower = text.lower()
	
	# Groom name
	groom_patterns = [
		r"groom['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
		r"groom[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
	]
	for pattern in groom_patterns:
		match = re.search(pattern, text, re.IGNORECASE)
		if match:
			entities["groom_name"] = match.group(1).strip()
			break
	
	# Bride name
	bride_patterns = [
		r"bride['\s]*s?\s+name[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
		r"bride[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)",
	]
	for pattern in bride_patterns:
		match = re.search(pattern, text, re.IGNORECASE)
		if match:
			entities["bride_name"] = match.group(1).strip()
			break
	
	# Marriage date
	marriage_date_patterns = [
		r"marriage\s+date[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})",
		r"married\s+on[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})",
		r"wedding\s+date[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})",
	]
	for pattern in marriage_date_patterns:
		match = re.search(pattern, text, re.IGNORECASE)
		if match:
			try:
				parsed = date_parser.parse(match.group(1), dayfirst=True, fuzzy=True)
				entities["marriage_date"] = parsed.strftime("%d-%m-%Y")
			except Exception:
				pass
			break
	
	return entities


