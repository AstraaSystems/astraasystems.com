export async function estimate(data) {
  const res = await fetch("http://127.0.0.1:5000/estimate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-KEY": "astraa_secure"
    },
    body: JSON.stringify(data)
  });

  return await res.json();
}
