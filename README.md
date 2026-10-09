# 📱 USA Phone Validator & Proxy Automation (Web & Neon Database)

A powerful Web Application that integrates **Scamalytics Free IP Reputation**, **NANP Area Code Matching**, **Veriphone Real Mobile SIM Verification**, **Google AI Studio Gemini 3.5 Flash Lite** persona copywriter, and **Neon PostgreSQL Database** integration ready for **Vercel** deployment.

---

## 🚀 Features

- 🛡️ **Scamalytics Free IP Reputation**: IP fraud score, trust score, ISP, ASN, Postal Code, Timezone, and threat flags (Proxy, VPN, Tor, Datacenter).
- 📱 **Real Mobile SIM Auto-Matcher**: Generates NANP candidate numbers matching the proxy location and tests them in a loop until a genuine mobile SIM is verified (auto-stops on match).
- 📋 **Clean Number Copy**: Copies the 10-digit number directly without the `+1` prefix.
- ✨ **Gemini 3.5 Flash Lite Persona Studio**: Generates realistic dating/social headlines and post bios with full emoji support (🌙, ✨, 🥂, 🔥, ☕, 🚀).
- 📅 **Smart DOB & Age**: Select Year (`1950 - 2005`) and Month name (`January - December`); age is automatically calculated in real time (no age dropdown needed).
- 💾 **Neon PostgreSQL Database**:
  - Save any verified profile with one click (`💾 Save to Database`).
  - Stores: Phone number, Carrier, IP address, Location, Fraud score, DOB, Age, Headline, Post/Bio, and timestamp.
  - Slide-over drawer (`📁 Saved Profiles`) to browse, search, copy, delete, and export records as CSV anytime.
  - Fallback to local storage if Neon DB is not yet connected.
- ⚡ **Vercel Serverless Ready**: Full serverless API backend in `api/` configured for Vercel.

---

## 🛠️ Quick Local Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment Variables** (Optional for local Neon DB):
   Create a `.env` file from `.env.example`:
   ```bash
   DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-YOUR-PROJECT.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

3. **Start the local server**:
   ```bash
   npm start
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ☁️ Deploy to Vercel (1-Click or Git)

1. Push this project to your **GitHub** repository (see instructions below).
2. Go to [Vercel](https://vercel.com) and click **"Add New Project"**.
3. Import your GitHub repository.
4. In the **Environment Variables** section, add:
   - `DATABASE_URL`: Your Neon PostgreSQL Connection String (from [Neon Console](https://console.neon.tech)).
   - `VERIPHONE_KEY`: (Optional) Your Veriphone API Key.
   - `AI_STUDIO_KEY`: (Optional) Your Gemini AI Studio Key.
5. Click **"Deploy"**! Your live web application with full Neon database persistence will be running in seconds.

---

## 🐙 Push to GitHub Instructions

```bash
git init
git add .
git commit -m "Initial commit: USA Phone Validator Web App with Neon DB & Vercel deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```
