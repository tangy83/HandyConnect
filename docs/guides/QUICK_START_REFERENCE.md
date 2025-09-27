# HandyConnect - Quick Start Reference Card

**For Swetha - Keep this handy! 📌**

---

## 🚀 **Daily Commands**

```bash
# Start development
source venv/bin/activate
python app.py

# Run tests
python -m pytest tests/ -v

# Check API health
curl http://localhost:5001/api/test/configuration
curl -X POST http://localhost:5001/api/test/email-access

# Git workflow
git pull origin main
git checkout swetha-development
git add .
git commit -m "Your changes"
git push origin swetha-development
```

---

## 📧 **Test Email Address**

**Send test emails to:**
`support@handyconnectdev.onmicrosoft.com`

---

## 🔑 **Important Files**

- **Main app**: `app.py`
- **Configuration**: `.env`
- **Your work area**: `features/`
- **Tests**: `tests/`
- **Documentation**: `docs/`

---

## 🆘 **Quick Fixes**

**Port 5001 in use:**
```bash
pkill -f "python app.py"
```

**Reset virtual environment:**
```bash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Check logs:**
```bash
tail -f logs/app.log
```

---

## 🎯 **Your Focus Areas**

- **Phase 6**: Frontend UI components
- **Phase 7**: User authentication
- **Phase 8**: Advanced email features

---

## 📞 **Need Help?**

1. Check `docs/` folder
2. Search codebase
3. Ask the team!

**Happy coding! 🚀**
