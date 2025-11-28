import pandas as pd

class SimpleEventRecommender:
  def __init__(self, events_df: pd.DataFrame):
    self.events_df = events_df.copy()
    # normalize category text
    self.events_df["category"] = self.events_df["category"].fillna("").astype(str).str.strip()
    
  def score_event_for_users(self, event_row, user_profiles):
    """Return a 0..1 score for how well event_row fits the list of user_profiles.
    user_profiles: list of dicts with 'user_id' and 'preferences' (list of strings)
    """
    scores = []
    desc = str(event_row.get("description", "")).lower()
    cat = str(event_row.get("category", "")).lower()
    for u in user_profiles:
      prefs = [p.lower() for p in u.get("preferences", [])]
      score = 0.0
      if cat in prefs and cat != "":
        score += 1.0
      # keyword hits
      hits = sum(1 for p in prefs if p in desc)
      if hits:
        score += 0.5
      scores.append(min(score, 1.0))
  return sum(scores) / len(scores) if scores else 0.0
  
  def rank_events_for_users(self, user_profiles, slot_start=None, slot_end=None, top_n=5):
    df = self.events_df.copy()
    if slot_start is not None and slot_end is not None:
      # optionally filter events that overlap slot or are near the slot
      # Here we select events that start within +/- 1 day of slot start OR events that fit within slot
      df = df[~df["start"].isna()]
      df = df[(df["start"] >= (slot_start - pd.Timedelta(days=1))) & (df["start"] <= (slot_start + pd.Timedelta(days=1))) |
              ((df["start"] >= slot_start) & (df["end"] <= slot_end))]
    df = df.copy()
    df["match_score"] = df.apply(lambda r: self.score_event_for_users(r, user_profiles), axis=1)
    return df.sort_values("match_score", ascending=False).head(top_n)
