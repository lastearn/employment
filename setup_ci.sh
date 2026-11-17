#!/bin/bash
# One-time setup of automatic deploys (run in Google Cloud Shell).
set -e
P=employment-trainer
SA=github-deployer@$P.iam.gserviceaccount.com
gcloud config set project $P >/dev/null
gcloud iam service-accounts describe $SA >/dev/null 2>&1 || \
  gcloud iam service-accounts create github-deployer --display-name="GitHub deploy (hosting only)"
for R in roles/firebasehosting.admin roles/serviceusage.serviceUsageConsumer; do
  gcloud projects add-iam-policy-binding $P --member=serviceAccount:$SA --role=$R --condition=None -q >/dev/null
done
KEY=$(mktemp)
gcloud iam service-accounts keys create "$KEY" --iam-account=$SA
echo
echo ">>> Сейчас появится код. Открой https://github.com/login/device, введи его и нажми Authorize."
gh auth login --hostname github.com --git-protocol https --web --scopes repo
gh secret set FIREBASE_SERVICE_ACCOUNT --repo lastearn/employment < "$KEY"
shred -u "$KEY" 2>/dev/null || rm -f "$KEY"
gh auth logout --hostname github.com >/dev/null 2>&1 || true
echo ">>> ГОТОВО: секрет сохранён, автовыкладка настроена."
