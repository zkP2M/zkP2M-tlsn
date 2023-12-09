# Notarize Merchant RazorPay Payments

## Notarize

```sh
RUST_LOG=debug,yamux=info cargo run --release --example razorpay_payment_proover
```

# Verifier


```
cargo run --release --example razorpay_payment_verifier
```


```log
curl -u rzp_test_c4bTc9bMwdE8xe:Eh6iHh3OyK7MTWFAljNXgHPS \
-X GET https://api.razorpay.com/v1/payments/pay_N9usRAfmAt1BJH

==RESP==

{"id":"pay_N9usRAfmAt1BJH","entity":"payment","amount":100,"currency":"INR","status":"captured","order_id":null,"invoice_id":null,"international":false,"method":"bank_transfer","amount_refunded":0,"refund_status":null,"captured":true,"description":"","card_id":null,"bank":null,"wallet":null,"vpa":null,"email":"hack@theplanet.com","contact":null,"customer_id":"cust_N9n8oiDOgKOPmk","notes":[],"fee":1,"tax":0,"error_code":null,"error_description":null,"error_source":null,"error_step":null,"error_reason":null,"acquirer_data":{},"created_at":1702052754}%
```
