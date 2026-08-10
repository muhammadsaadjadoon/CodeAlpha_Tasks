# Privacy and Storage

The backend database stores account data, password hashes, server-side sessions, theme preference, profile-picture bytes, and recognition-result metadata.

It does **not** store uploaded handwriting images, drawing-canvas images, processed previews, or plaintext passwords.

The frontend does not use `localStorage`, `sessionStorage`, or IndexedDB for user data. Authentication uses an HttpOnly SameSite session cookie. Authenticated API and profile-image responses use `Cache-Control: no-store`.
