# Stripe Supporter Membership - Setup Checklist

## Stripe Dashboard Setup

- [ ] Create a Stripe account at https://stripe.com (if not already done)
- [ ] Create a "Supporter" product in the Stripe Dashboard
- [ ] Create a recurring monthly price on that product with "Customer chooses what to pay" enabled
  - Set a minimum (e.g., $1/month)
  - Set a suggested preset (e.g., $5/month)
- [ ] Note the Price ID (e.g., `price_1Abc...`)
- [ ] Enable the Customer Portal in Settings > Billing > Customer Portal
  - Enable "Cancel subscription"
  - Enable "Update payment method"
  - Set return URL to `https://studyreformed.com/accounts/dashboard/`
- [ ] Add a webhook endpoint pointing to `https://studyreformed.com/accounts/support/webhook/`
  - Select events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`
  - Note the webhook signing secret (`whsec_...`)

## Render Environment Variables

Set these in the Render dashboard (not in code):

- [ ] `STRIPE_PUBLISHABLE_KEY` — your live publishable key (`pk_live_...`)
- [ ] `STRIPE_SECRET_KEY` — your live secret key (`sk_live_...`)
- [ ] `STRIPE_WEBHOOK_SECRET` — the webhook signing secret (`whsec_...`)
- [ ] `STRIPE_PRICE_ID` — the Price ID from the product you created (`price_...`)

## Local Testing (Optional)

- [ ] Install the Stripe CLI: `brew install stripe/stripe-cli/stripe`
- [ ] Run `stripe login`
- [ ] Set test keys in your local `.env` file
- [ ] Forward webhooks locally: `stripe listen --forward-to localhost:8000/accounts/support/webhook/`
- [ ] Set the `whsec_...` from the CLI output as `STRIPE_WEBHOOK_SECRET` in `.env`
- [ ] Run `python manage.py runserver` and test the full flow at `/accounts/support/`
- [ ] Trigger test events: `stripe trigger checkout.session.completed`

## Deploy

- [ ] Deploy to Render (migration runs automatically via `build.sh`)
- [ ] Verify the support page loads at `https://studyreformed.com/accounts/support/`
- [ ] Do a real end-to-end test with Stripe's test card (`4242 4242 4242 4242`)
- [ ] Verify the supporter badge appears in the navbar after subscribing
- [ ] Verify "Manage Subscription" redirects to the Stripe Customer Portal
