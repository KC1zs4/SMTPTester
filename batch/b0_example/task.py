TEMPLATES = {
    "simple_mail": [
        b"EHLO {ehlo}\r\n",
        b"MAIL FROM:<{mail_from}>\r\n",
        b"RCPT TO:<{rcpt_to}>\r\n",
        b"DATA\r\n",
        b"Subject: {subject}\r\nFrom: {mail_from}\r\nTo: {rcpt_to}\r\n\r\n{body}\r\n.\r\n",
        b"QUIT\r\n",
    ],

    "noop_probe": [
        b"EHLO {ehlo}\r\n",
        b"NOOP\r\n",
        b"QUIT\r\n",
    ],

    "timeout": [
        b"EHLO {ehlo}",
    ]
}

TASKS = [

    {
        "name": "test_mail",
        "template": "simple_mail",
        "values": {
            "ehlo": b"default.com",
            "mail_from": b"test-114514@default.com",
            "rcpt_to": b"test-114514@163.com",
            "subject": b"send mail test",
            "body": "你好".encode("utf-8") + b" from smtp tester\n.dot stuff test",
        },
    },

    {
        "name": "noop_check",
        "template": "noop_probe",
        "values": {
            "ehlo": b"default.com",
        },
    },

    {
        "name": "timeout_test",
        "template": "timeout",
        "values": {
            "ehlo": b"default.com",
        }
    }
]
