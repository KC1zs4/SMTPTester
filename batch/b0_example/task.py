TEMPLATES = {
    "normal_mail": [
        b"EHLO {ehlo}\r\n",
        b"MAIL FROM:<{mail_from}>\r\n",
        b"RCPT TO:<{rcpt_to}>\r\n",
        b"DATA\r\n",

        b"Subject: {subject}\r\n"
        b"From: {mail_from}\r\n"
        b"To: {rcpt_to}\r\n"
        b"\r\n"
        b"{body}\r\n"
        b".\r\n",

        b"QUIT\r\n",
    ],

    "noop_probe": [
        b"EHLO {ehlo}\r\n",
        b"NOOP\r\n",
        b"QUIT\r\n",
    ],

    "ehlo_timeout": [
        b"EHLO {ehlo}",
    ]
}

TASKS = [

    {
        "name": "send_mail_test",
        "template": "normal_mail",
        "values": {
            "ehlo": b"default.com",
            "mail_from": b"test-114514@default.com",
            "rcpt_to": b"test-114514@example.com",
            "subject": b"send mail test",
            "body": "你好".encode("utf-8") +
                    b" from smtp tester default\n"
                    b".dot stuff test",
        },
        "targets": {
            "163.com": {
                "rcpt_to": b"user_at_163@163.com",
                "body": "你好".encode("utf-8") +
                        b" from smtp tester 163.com\n"
                        b".dot stuff test",
            },
            "qq.com": {
                "rcpt_to": b"user_at_qq@qq.com",
                "body": "你好".encode("utf-8") +
                    b" from smtp tester qq.com\n"
                    b".dot stuff test",
            },
        },
    },

    {
        "name": "noop_test",
        "template": "noop_probe",
        "values": {
            "ehlo": b"default.com",
        },
    },

    {
        "name": "timeout_test",
        "template": "ehlo_timeout",
        "values": {
            "ehlo": b"default.com",
        }
    }
]
