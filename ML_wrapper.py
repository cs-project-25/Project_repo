def generate_invitation(slot_start, slot_end, free_users, top_events):
  """Return a list of 2 suggested invitation texts based on inputs. This is a placeholder stub.
  Replace with real LLM invocation.
  """
  user_names = ", ".join([u.get("name", str(u.get("user_id"))) for u in free_users])
  texts = []
  for tone in ("locker", "formell"):
    ev = top_events[0] if top_events else {"name": "(kein Event)", "description": ""}
    t = f"({tone}) Hallo {user_names}, wie wäre es mit '{ev['name']}' am {slot_start.strftime('%Y-%m-%d %H:%M')}?\nWarum: {ev.get('description','')[:120]}"
    texts.append({"tone": tone, "text": t})
  return texts
