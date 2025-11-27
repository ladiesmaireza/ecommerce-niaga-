const express = require("express");
const app = express();
const PORT = 4000;

app.use(express.json());

app.use(express.static("public"));

let users = [
  { id: 1, name: "Alice", email: "alice@example.com", role: "customer" },
  { id: 2, name: "Bob", email: "bob@example.com", role: "seller" },
  { id: 3, name: "Charlie", email: "charlie@example.com", role: "admin" },
];

app.get("/users", (req, res) => {
  res.json(users);
});

app.get("/users/:id", (req, res) => {
  const userId = parseInt(req.params.id);
  const user = users.find((u) => u.id === userId);

  if (!user) {
    return res.status(404).json({ message: "User tidak ditemukan" });
  }

  res.json(user);
});

app.post("/users", (req, res) => {
    const { name, email, role } = req.body;

     if (!name || !email || !role) {
    return res.status(400).json({
      message: "Name, email, dan role wajib diisi!"
    });
  }

  const newUser = {
    id: users.length + 1,
    name,
    email,
    role,
  };

  users.push(newUser);
  res.status(201).json(newUser);
});

app.listen(PORT, () => {
  console.log(`User Service berjalan di http://localhost:${PORT}`);
});
