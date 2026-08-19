import pandas as pd
import random

platforms = ['Jupiter', 'GPay', 'PhonePe', 'Paytm', 'Razorpay']
faq_data = {
    'UPI': [
        ("How do I reset my UPI PIN?", "Go to 'Bank Account' in your app > Tap 'Reset UPI PIN'."),
        ("What is the daily UPI limit?", "Most apps allow ₹1,00,000 per day via UPI."),
        ("Can I link two bank accounts?", "Yes, multiple accounts can be linked under UPI."),
        ("Why did my UPI payment fail?", "Due to network issues or bank downtime. Try again later."),
    ],
    'Refunds': [
        ("When will I get my refund?", "Refunds typically take 5–7 business days."),
        ("How can I track a refund?", "Go to 'Transactions' > Select payment > Check refund status."),
        ("Why is my refund delayed?", "Some refunds may be held up due to bank processing."),
    ],
    'KYC': [
        ("How do I complete KYC?", "Go to Profile > KYC > Upload ID and address proof."),
        ("Why is KYC important?", "KYC is mandatory as per RBI guidelines to continue services."),
    ],
    'Card': [
        ("How do I activate my debit card?", "Open the Cards section > Tap 'Activate Card'."),
        ("How to block a lost card?", "Go to Card Settings > Tap 'Block Card' immediately."),
        ("Can I change my card PIN?", "Yes, from the 'Manage Card' option in your app."),
    ],
    'Security': [
        ("How to report a suspicious transaction?", "Tap on the transaction > Select 'Report'."),
        ("How do I enable app lock?", "Go to Settings > Security > Enable fingerprint or PIN lock."),
    ],
    'Payments': [
        ("How to pay using QR code?", "Tap 'Scan & Pay' > Point to merchant QR > Enter amount."),
        ("Can I schedule a payment?", "Yes, set up auto-pay in your bill payment settings."),
    ],
    'Bank Linking': [
        ("How do I link a bank account?", "Go to 'Add Bank' > Choose bank > Verify with OTP."),
        ("My bank is not listed. What should I do?", "Try later or contact support to raise a request."),
    ],
    'Recharge': [
        ("How can I recharge my mobile?", "Go to 'Recharge' > Enter number > Choose plan > Pay."),
        ("Can I set a recharge reminder?", "Yes, enable notifications under Recharge settings."),
    ],
    'Loans': [
        ("Can I get a personal loan?", "Check eligibility under 'Loans' > Apply if eligible."),
        ("What is the interest rate on loans?", "It varies by user profile and is shown before you apply."),
    ],
    'Wallet': [
        ("How do I add money to wallet?", "Tap 'Add Money' > Enter amount > Choose payment mode."),
        ("Why is wallet balance not updating?", "It could be a delay in syncing with the server."),
    ]
}

all_qas = []
for cat, pairs in faq_data.items():
    for q, a in pairs:
        all_qas.append((cat, q, a))

faq_entries = []
for _ in range(100):
    category, question, answer = random.choice(all_qas)
    faq_entries.append({
        "platform": random.choice(platforms),
        "category": category,
        "question": question,
        "answer": answer
    })

df = pd.DataFrame(faq_entries)
df.to_csv("random_faq_100.csv", index=False)
print("FAQs generated and saved to random_faq_100.csv")
print(df.sample(5))
