const BASE_URL = "http://localhost:8000/api";

const getEvents = async () => {
  const res = await fetch(`${BASE_URL}/events/`, { cache: "no-store" });
  return res.json();
};
