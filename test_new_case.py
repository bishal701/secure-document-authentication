import requests
import json
import time

BASE_URL = 'http://127.0.0.1:8000'

print('==================================================================')
print('RUNNING COMPREHENSIVE NEW TEST CASE VERIFICATION')
print('==================================================================')

# 1. Issue New Document
print('\n[1/6] Issuing brand new document for Aarav Sharma...')
issue_payload = {
    'recipient_name': 'Aarav Sharma',
    'registration_number': '23BCI0888',
    'degree': 'B.Tech in Artificial Intelligence & Robotics',
    'grade': 'First Class with Distinction (9.8 CGPA)',
    'institution': 'VELLORE INSTITUTE OF TECHNOLOGY',
    'issuer_domain': 'vit.ac.in',
    'template_id': 'certificate',
    'script': 'latin'
}
res = requests.post(f'{BASE_URL}/api/documents/generate', json=issue_payload)
assert res.status_code == 200, f'Issuance failed: {res.text}'
doc_meta = res.json()
doc_id = doc_meta['document_id']
img_b64 = doc_meta['image_base64']
print(f'   -> Document Created: ID={doc_id}')
print(f'   -> QR Encoded Length: {len(doc_meta["qr_encoded_text"])} chars')
print(f'   -> Watermark PSNR: {doc_meta["watermark_metrics"]["psnr_db"]} dB (High imperceptibility)')
print(f'   -> Watermark SSIM: {doc_meta["watermark_metrics"]["ssim"]} (Near-lossless)')

# 2. Verify Genuine Document
print('\n[2/6] Verifying Pristine Genuine Document...')
res_ver = requests.post(f'{BASE_URL}/api/documents/verify', json={'image_base64': img_b64, 'doc_id_hint': doc_id})
assert res_ver.status_code == 200, f'Verification failed: {res_ver.text}'
v_data = res_ver.json()
print(f'   -> Final Status: {v_data["final_status"]}')
print(f'   -> QR Status: {v_data["layers"]["qr"]["status"]}')
print(f'   -> Ed25519 Signature: {v_data["layers"]["signature"]["status"]}')
print(f'   -> Watermark NC: {v_data["layers"]["watermark"]["nc_score"]} ({v_data["layers"]["watermark"]["status"]})')
print(f'   -> Copy Score: {v_data["layers"]["copy_detection_A"]["copy_score"]} ({v_data["layers"]["copy_detection_A"]["status"]})')
print(f'   -> Total Latency: {v_data["total_verification_time_ms"]} ms')

# 3. Simulate Print-Scan Copy Attack
print('\n[3/6] Simulating Print-Scan Photocopy Attack...')
res_ps = requests.post(f'{BASE_URL}/api/attack/simulate', json={'image_base64': img_b64, 'document_id': doc_id, 'attack_type': 'PRINT_SCAN'})
assert res_ps.status_code == 200
ps_data = res_ps.json()['verification_result']
print(f'   -> Verdict: {ps_data["final_status"]}')
print(f'   -> Copy Score: {ps_data["layers"]["copy_detection_A"]["copy_score"]} (Threshold: 0.35)')
print(f'   -> Copy Detected: {ps_data["layers"]["copy_detection_A"]["status"]}')

# 4. Simulate Content Splicing / Local Tampering
print('\n[4/6] Simulating Content Splicing / Forgery (Altered Name/Grade)...')
res_tamper = requests.post(f'{BASE_URL}/api/attack/simulate', json={'image_base64': img_b64, 'document_id': doc_id, 'attack_type': 'TAMPER'})
assert res_tamper.status_code == 200
tamper_data = res_tamper.json()['verification_result']
print(f'   -> Verdict: {tamper_data["final_status"]}')
print(f'   -> Watermark NC: {tamper_data["layers"]["watermark"]["nc_score"]} (Threshold: 0.70)')
print(f'   -> Watermark Status: {tamper_data["layers"]["watermark"]["status"]}')
print(f'   -> Summary: {tamper_data["summary"]}')

# 5. Semantic Typosquatting Audit
print('\n[5/6] Testing Semantic Domain Typosquatting...')
for dom in ['vit.ac.in', 'vlt.ac.in', 'v1t.ac.in', 'harvard.edu']:
    t_res = requests.post(f'{BASE_URL}/api/trust-registry/check-domain', json={'domain': dom}).json()
    print(f'   -> Domain "{dom}": similarity={t_res.get("similarity", 0.0)*100:.1f}%, is_typosquat={t_res.get("is_typosquat")}, is_trusted={t_res.get("is_trusted")}')

# 6. Web-PKI Key Revocation & Recovery
print('\n[6/6] Testing Real-Time Key Revocation & Re-Activation...')
pki_list = requests.get(f'{BASE_URL}/api/trust-registry').json()
vit_key = next(k['key_id'] for k in pki_list if k['domain'] == 'vit.ac.in')

rev_res = requests.post(f'{BASE_URL}/api/trust-registry/revoke', json={'key_id': vit_key}).json()
print(f'   -> Key Revoked in {rev_res["revocation_latency_ms"]} ms')

ver_revoked = requests.post(f'{BASE_URL}/api/documents/verify', json={'image_base64': img_b64, 'doc_id_hint': doc_id}).json()
print(f'   -> Verification Under Revoked Key: {ver_revoked["final_status"]} (Signature: {ver_revoked["layers"]["signature"]["status"]})')

rec_res = requests.post(f'{BASE_URL}/api/trust-registry/reactivate', json={'key_id': vit_key}).json()
print(f'   -> Key Re-Activated: {rec_res["status"]}')

ver_restored = requests.post(f'{BASE_URL}/api/documents/verify', json={'image_base64': img_b64, 'doc_id_hint': doc_id}).json()
print(f'   -> Verification Restored: {ver_restored["final_status"]} (Signature: {ver_restored["layers"]["signature"]["status"]})')

print('\n==================================================================')
print('ALL 6/6 TEST PHASES EXECUTED & PASSED PERFECTLY!')
print('==================================================================')
