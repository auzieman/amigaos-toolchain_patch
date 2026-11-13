"""Require the qualified compiler identity when accepting final target builds."""
def matches_qualified_compiler(record, policy):
    evidence = record.get('compiler', {})
    digest = policy.get('qualified_sdk_receipt_sha256')
    return bool(
        policy.get('qualification_status') == 'passed'
        and policy.get('required_gcc_major') == 14
        and digest
        and evidence.get('gcc_major') == 14
        and evidence.get('sdk_receipt_sha256') == digest
    )
