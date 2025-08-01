| Feature                | **HTTP/1.1**                             | **HTTP/2**                   | **HTTP/3**                                  |
| ---------------------- | ---------------------------------------- | ---------------------------- | ------------------------------------------- |
| Released               | 1999                                     | 2015                         | 2022 (based on QUIC)                        |
| Protocol Type          | TCP                                      | TCP                          | UDP + QUIC                                  |
| Performance            | 🚫 Slower                                | ⚡ Faster than HTTP/1.1       | 🚀 Even faster, low-latency                 |
| Parallel Requests      | 🚫 One request per connection (blocking) | ✅ Multiplexed (many at once) | ✅ Multiplexed without head-of-line blocking |
| Header Compression     | ❌ None                                   | ✅ Yes (HPACK)                | ✅ Yes (QPACK)                               |
| TLS Encryption         | Optional (via HTTPS)                     | Required (via HTTPS)         | ✅ Always encrypted (built-in TLS)           |
| Connection Reuse       | ✅ Keep-Alive                             | ✅ Better via streams         | ✅ Best (QUIC enables faster reuse)          |
| Deployment Requirement | ✅ Easy to use everywhere                 | ✅ Supported by most servers  | 🟡 Requires server/network support          |
