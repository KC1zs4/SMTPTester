TEMPLATES = {
    "simple_mail": [
        {"data": "EHLO {ehlo}\r\n"},
        {"data": "MAIL FROM:<{mail_from}>\r\n"},
        {"data": "RCPT TO:<{rcpt_to}>\r\n"},
        {"data": "DATA\r\n"},
        {
            "data": "Subject: {subject}\r\nFrom: {mail_from}\r\nTo: {rcpt_to}\r\n\r\n{body}\r\n",
            "expect_response": True,
        },
        {"data": ".\r\n"},
        {"data": "QUIT\r\n"},
    ],

    "noop_probe": [
        {"data": "EHLO {ehlo}\r\n"},
        {"data": "NOOP\r\n"},
        {"data": "QUIT\r\n"},
    ],

    "timeout": [
        {"data": "EHLO {ehlo}"},
    ]
}

TASKS = [

    {
        "name": "test_mail",
        "template": "simple_mail",
        "values": {
            "ehlo": "default.com",
            "mail_from": "test-114514@default.com",
            "rcpt_to": "test-114514@163.com",
            "subject": "send mail test",
            "body": "hello from smtp tester\n.dot stuff test",
        },
    },

    {
        "name": "noop_check",
        "template": "noop_probe",
        "values": {
            "ehlo": "default.com",
        },
    },

    {
        "name": "timeout_test",
        "template": "timeout",
        "values": {
            "ehlo": "default.com",
        }
    }
]