# Requirement Traceability

| Internship requirement | WriteLens implementation |
|---|---|
| Identify handwritten characters or alphabets | Upload + drawing canvas + CNN inference |
| Image processing | grayscale, alpha compositing, polarity correction, denoising, thresholding, foreground crop, deskew, square padding, centering, 28×28 resize |
| Deep learning | custom CNN trained from scratch |
| MNIST | dedicated digit specialist |
| EMNIST | Balanced benchmark + ByClass 62-class model |
| CNN | `ml/models/cnn.py` |
| Extendable to words/sentences | CRNN + BiLSTM + CTC in `ml/models/crnn.py` and `train_crnn.py` |
| Professional usable app | React/TypeScript frontend + FastAPI backend |
| Light/dark themes | server-owned theme preference |
| Authentication | database-backed accounts + HttpOnly session cookie |
| No browser/local persistence | user data stays backend-side; input images are not retained |
