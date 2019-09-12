

class User:

    def __init__(self, json):
        self.id = int(json.get("user_id"))
        self.name = json.get("username")
        self.join_date = json.get("join_date")
        self.count300 = int(json.get("count300"))
        self.count100 = int(json.get("count100"))
        self.count50 = int(json.get("count50"))
        self.playcount = int(json.get("playcount"))
        self.ranked_score = json.get("ranked_score")
        self.total_score = json.get("total_score")
        self.pp_rank = int(json.get("pp_rank"))
        self.level = float(json.get("level"))
        self.pp_raw = json.get("pp_raw")
        self.accuracy = float(json.get("accuracy"))
        self.count_rank_ss = json.get("count_rank_ss")
        self.count_rank_ssh = json.get("count_rank_ssh")
        self.count_rank_s = json.get("count_rank_s")
        self.count_rank_sh = json.get("count_rank_sh")
        self.count_rank_a = json.get("count_rank_a")
        self.country = json.get("country")
        self.total_seconds_played = int(json.get("total_seconds_played"))
        self.pp_country_rank = json.get("pp_country_rank")
        self.events = json.get("events")

    def __repr__(self):
        return "<{0.__module__}.User username={0.name} user_id={0.id}>".format(self)

    def __str__(self):
        return self.name
