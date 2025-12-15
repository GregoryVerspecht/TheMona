async function postJson(form, body) {
  const res = await fetch(form.action, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  if (!res.ok) alert('Request failed');
  location.reload();
  return false;
}
