from deadline_radar.extract import extract, extract_deadline, extract_prize


def test_devpost_like_page(load_fixture):
    info = extract(load_fixture("devpost_like.html"))
    assert info["title"] == "Build With AI: Basics | Devpost"
    # "Submissions close October 26, 2026" beats the other dates on the page.
    assert info["deadline"] == "2026-10-26"
    assert info["prize"] == "$2,500"


def test_grant_like_page(load_fixture):
    info = extract(load_fixture("grant_like.html"))
    assert info["title"] == "Community Innovation Grant Program"
    assert info["deadline"] == "2026-11-15"
    # $10,000 near "award"/"funding" beats the $5 processing fee.
    assert info["prize"] == "$10,000"


def test_page_without_deadline_or_prize(load_fixture):
    info = extract(load_fixture("no_deadline.html"))
    assert info["title"] == "About Our Organization"
    assert info["deadline"] is None
    assert info["prize"] is None


def test_malformed_html_never_raises(load_fixture):
    info = extract(load_fixture("malformed.html"))
    assert info["deadline"] is None
    assert info["prize"] is None


def test_script_and_style_bodies_are_ignored(load_fixture):
    # The fixture's <script> contains a decoy "deadline 1999-01-01".
    info = extract(load_fixture("devpost_like.html"))
    assert info["deadline"] != "1999-01-01"


def test_us_numeric_date_format():
    assert extract_deadline("Entries are due 10/26/2026 at midnight.") == "2026-10-26"


def test_day_first_month_name_format():
    assert extract_deadline("The competition closes 5 January 2027.") == "2027-01-05"


def test_iso_date_format():
    assert extract_deadline("Apply by 2027-03-01 for consideration.") == "2027-03-01"


def test_date_far_from_any_keyword_is_ignored():
    text = "Founded in 1998. " + ("padding " * 60) + "Something happened 2015-06-30."
    assert extract_deadline(text) is None


def test_prize_requires_keyword_proximity():
    text = "Tickets cost $99. " + ("padding " * 60) + "Nothing else here."
    assert extract_prize(text) is None


def test_largest_amount_near_prize_keywords_wins():
    text = "Prizes: $500 for second place, $1,000 for the winner."
    assert extract_prize(text) == "$1,000"
