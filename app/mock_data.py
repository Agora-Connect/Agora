from datetime import datetime, timezone, timedelta


def dt(minutes_ago=0, hours_ago=0, days_ago=0):
    return datetime.now(timezone.utc) - timedelta(
        minutes=minutes_ago, hours=hours_ago, days=days_ago
    )


# ──────────────────────────────────────────────
# CURRENT USER (logged-in session)
# ──────────────────────────────────────────────
CURRENT_USER = {
    'id': 1,
    'username': 'arsalan_uw',
    'display_name': 'Arsalan Anwer',
    'email': 'arsalan@uw.edu',
    'university': 'University of Washington',
    'major': 'Computer Science',
    'year': 'Junior',
    'bio': 'CS @ UW | Databases, systems, and coffee ☕',
    'location': 'Seattle, WA',
    'website': 'arsalan.dev',
    'avatar_url': None,
    'banner_url': None,
    'reputation_score': 342,
    'is_verified': False,
    'followers_count': 128,
    'following_count': 74,
    'joined_at': dt(days_ago=420),
}

# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────
USERS = [
    {
        'id': 2,
        'username': 'sara_cs411',
        'display_name': 'Sara Malik',
        'email': 'sara@uw.edu',
        'university': 'University of Washington',
        'major': 'Computer Science',
        'year': 'Senior',
        'bio': 'Senior CS student. Love databases and distributed systems.',
        'location': 'Seattle, WA',
        'website': '',
        'avatar_url': None,
        'reputation_score': 891,
        'is_verified': True,
        'followers_count': 412,
        'following_count': 98,
        'joined_at': dt(days_ago=600),
        'is_following': True,
    },
    {
        'id': 3,
        'username': 'jpark_math',
        'display_name': 'Jason Park',
        'email': 'jpark@uw.edu',
        'university': 'University of Washington',
        'major': 'Mathematics',
        'year': 'Sophomore',
        'bio': 'Math major figuring out life one proof at a time.',
        'location': 'Seattle, WA',
        'website': '',
        'avatar_url': None,
        'reputation_score': 120,
        'is_verified': False,
        'followers_count': 45,
        'following_count': 61,
        'joined_at': dt(days_ago=200),
        'is_following': False,
    },
    {
        'id': 4,
        'username': 'priya_ece',
        'display_name': 'Priya Sharma',
        'email': 'priya@uw.edu',
        'university': 'University of Washington',
        'major': 'Electrical & Computer Engineering',
        'year': 'Graduate',
        'bio': 'MS ECE | Research in ML systems.',
        'location': 'Seattle, WA',
        'website': 'priya.io',
        'avatar_url': None,
        'reputation_score': 1240,
        'is_verified': True,
        'followers_count': 830,
        'following_count': 210,
        'joined_at': dt(days_ago=730),
        'is_following': True,
    },
    {
        'id': 5,
        'username': 'mike_info',
        'display_name': 'Mike Torres',
        'email': 'mike@uw.edu',
        'university': 'University of Washington',
        'major': 'Informatics',
        'year': 'Junior',
        'bio': 'Informatics junior. UI/UX enthusiast.',
        'location': 'Bellevue, WA',
        'website': '',
        'avatar_url': None,
        'reputation_score': 205,
        'is_verified': False,
        'followers_count': 87,
        'following_count': 112,
        'joined_at': dt(days_ago=310),
        'is_following': False,
    },
]

# ──────────────────────────────────────────────
# COURSES
# ──────────────────────────────────────────────
COURSES = [
    {'id': 1, 'code': 'CSCI 411', 'name': 'Database Systems', 'enrolled': True},
    {'id': 2, 'code': 'CSCI 351', 'name': 'Data Structures & Algorithms', 'enrolled': True},
    {'id': 3, 'code': 'MATH 221', 'name': 'Linear Algebra', 'enrolled': True},
    {'id': 4, 'code': 'CSCI 421', 'name': 'Operating Systems', 'enrolled': False},
    {'id': 5, 'code': 'CSCI 461', 'name': 'Computer Networks', 'enrolled': False},
]

# ──────────────────────────────────────────────
# POSTS
# ──────────────────────────────────────────────
POSTS = [
    {
        'id': 1,
        'author': USERS[0],  # sara_cs411
        'course': COURSES[0],
        'content': 'Just finished the ER diagram for our CSCI 411 project. Normalization to 3NF is no joke — spent 3 hours eliminating transitive dependencies 😅 Anyone else working on the Agora project?',
        'is_anonymous': False,
        'images': [],
        'tags': ['databases', 'csci411', 'normalization'],
        'like_count': 24,
        'repost_count': 3,
        'reply_count': 8,
        'is_liked_by_me': False,
        'is_reposted_by_me': False,
        'is_bookmarked_by_me': True,
        'created_at': dt(hours_ago=2),
    },
    {
        'id': 2,
        'author': USERS[3],  # priya_ece
        'course': COURSES[1],
        'content': 'Quick tip for CSCI 351: when implementing Dijkstra\'s, use a min-heap (priority queue) instead of a plain array. Drops time complexity from O(V²) to O((V+E) log V). Huge difference on dense graphs.',
        'is_anonymous': False,
        'images': [],
        'tags': ['csci351', 'algorithms', 'tip'],
        'like_count': 67,
        'repost_count': 21,
        'reply_count': 12,
        'is_liked_by_me': True,
        'is_reposted_by_me': False,
        'is_bookmarked_by_me': False,
        'created_at': dt(hours_ago=5),
    },
    {
        'id': 3,
        'author': USERS[1],  # jpark_math
        'course': COURSES[2],
        'content': 'Does anyone have good notes on eigenvalues and eigenvectors from MATH 221? Our midterm is on Friday and I feel completely lost on the geometric interpretation.',
        'is_anonymous': False,
        'images': [],
        'tags': ['math221', 'midterm', 'eigenvalues'],
        'like_count': 11,
        'repost_count': 1,
        'reply_count': 5,
        'is_liked_by_me': False,
        'is_reposted_by_me': False,
        'is_bookmarked_by_me': False,
        'created_at': dt(hours_ago=8),
    },
    {
        'id': 4,
        'author': {'id': 99, 'username': 'anonymous', 'display_name': 'Anonymous', 'avatar_url': None, 'is_verified': False},
        'course': COURSES[0],
        'content': 'Hot take: professors who don\'t release past exams are actively making education worse. If you want students to learn the material, show them what mastery looks like.',
        'is_anonymous': True,
        'images': [],
        'tags': ['campuslife', 'education'],
        'like_count': 143,
        'repost_count': 38,
        'reply_count': 29,
        'is_liked_by_me': True,
        'is_reposted_by_me': False,
        'is_bookmarked_by_me': False,
        'created_at': dt(hours_ago=14),
    },
    {
        'id': 5,
        'author': USERS[0],  # sara_cs411
        'course': COURSES[0],
        'content': 'PSA: The Allen Library study rooms are fully booked for the next 2 weeks. Book early for finals! Also the 4th floor has new standing desks 🙌',
        'is_anonymous': False,
        'images': [],
        'tags': ['campuslife', 'library', 'finals'],
        'like_count': 89,
        'repost_count': 44,
        'reply_count': 7,
        'is_liked_by_me': False,
        'is_reposted_by_me': True,
        'is_bookmarked_by_me': False,
        'created_at': dt(days_ago=1),
    },
    {
        'id': 6,
        'author': USERS[2],  # mike_info
        'course': COURSES[1],
        'content': 'Study group for CSCI 351 final exam forming now! Meeting Wed 6pm @ Odegaard 2nd floor. We\'ll go through sorting, graphs, and dynamic programming. Drop a reply if you\'re in!',
        'is_anonymous': False,
        'images': [],
        'tags': ['csci351', 'studygroup', 'finals'],
        'like_count': 32,
        'repost_count': 9,
        'reply_count': 15,
        'is_liked_by_me': False,
        'is_reposted_by_me': False,
        'is_bookmarked_by_me': True,
        'created_at': dt(days_ago=2),
    },
]

# ──────────────────────────────────────────────
# PROBLEMS (Q&A Forum)
# ──────────────────────────────────────────────
PROBLEMS = [
    {
        'id': 1,
        'author': USERS[1],
        'course': COURSES[0],
        'title': 'Why does BCNF decomposition lose dependency preservation?',
        'description': 'I understand that BCNF eliminates all anomalies but I keep reading that it doesn\'t always preserve functional dependencies. Can someone explain with a concrete example?',
        'tags': ['databases', 'bcnf', 'normalization'],
        'answer_count': 3,
        'has_accepted_answer': True,
        'upvote_count': 18,
        'is_upvoted_by_me': False,
        'created_at': dt(hours_ago=6),
    },
    {
        'id': 2,
        'author': USERS[2],
        'course': COURSES[1],
        'title': 'Time complexity of building a heap vs sorting with a heap?',
        'description': 'I know heapsort is O(n log n) but I read that building a heap from an array is O(n). How can building be faster than sorting if sorting uses the heap?',
        'tags': ['csci351', 'heaps', 'complexity'],
        'answer_count': 2,
        'has_accepted_answer': False,
        'upvote_count': 9,
        'is_upvoted_by_me': True,
        'created_at': dt(hours_ago=12),
    },
    {
        'id': 3,
        'author': USERS[0],
        'course': COURSES[2],
        'title': 'Geometric meaning of the null space of a matrix?',
        'description': 'I can compute the null space but I don\'t understand what it actually represents geometrically. How should I think about it visually?',
        'tags': ['math221', 'linear-algebra', 'null-space'],
        'answer_count': 4,
        'has_accepted_answer': True,
        'upvote_count': 25,
        'is_upvoted_by_me': False,
        'created_at': dt(days_ago=1),
    },
]

# ──────────────────────────────────────────────
# NOTIFICATIONS
# ──────────────────────────────────────────────
NOTIFICATIONS = [
    {
        'id': 1,
        'type': 'like',
        'actors': [USERS[0]],
        'message': 'liked your post',
        'post_preview': 'Just finished the ER diagram for our CSCI 411 project...',
        'is_read': False,
        'created_at': dt(minutes_ago=15),
    },
    {
        'id': 2,
        'type': 'follow',
        'actors': [USERS[3]],
        'message': 'followed you',
        'post_preview': None,
        'is_read': False,
        'created_at': dt(hours_ago=1),
    },
    {
        'id': 3,
        'type': 'reply',
        'actors': [USERS[0]],
        'message': 'replied to your post',
        'post_preview': 'Yes! I used BCNF for our schema too...',
        'is_read': False,
        'created_at': dt(hours_ago=3),
    },
    {
        'id': 4,
        'type': 'like',
        'actors': [USERS[1], USERS[2], USERS[3]],
        'message': 'and 2 others liked your post',
        'post_preview': 'Study group for CSCI 351 final exam forming now!...',
        'is_read': False,
        'created_at': dt(hours_ago=5),
    },
    {
        'id': 5,
        'type': 'repost',
        'actors': [USERS[2]],
        'message': 'reposted your post',
        'post_preview': 'PSA: The Allen Library study rooms are fully booked...',
        'is_read': True,
        'created_at': dt(days_ago=1),
    },
    {
        'id': 6,
        'type': 'answer',
        'actors': [USERS[0]],
        'message': 'answered your question',
        'post_preview': 'BCNF decomposition loses dependency preservation when...',
        'is_read': True,
        'created_at': dt(days_ago=2),
    },
]

# ──────────────────────────────────────────────
# MESSAGES / CONVERSATIONS
# ──────────────────────────────────────────────
CONVERSATIONS = [
    {
        'id': 1,
        'participant': USERS[0],  # sara
        'last_message': 'Are you coming to the study group on Wednesday?',
        'last_message_at': dt(minutes_ago=30),
        'is_unread': True,
        'messages': [
            {'id': 1, 'sender_id': 2, 'content': 'Hey! Did you finish the CSCI 411 project?', 'sent_at': dt(hours_ago=2)},
            {'id': 2, 'sender_id': 1, 'content': 'Almost! Just need to finalize the ER diagram. You?', 'sent_at': dt(hours_ago=1, minutes_ago=45)},
            {'id': 3, 'sender_id': 2, 'content': 'Done! It took forever to get 3NF right.', 'sent_at': dt(hours_ago=1, minutes_ago=30)},
            {'id': 4, 'sender_id': 2, 'content': 'Are you coming to the study group on Wednesday?', 'sent_at': dt(minutes_ago=30)},
        ],
    },
    {
        'id': 2,
        'participant': USERS[3],  # priya
        'last_message': 'Thanks for the Dijkstra tip!',
        'last_message_at': dt(hours_ago=4),
        'is_unread': False,
        'messages': [
            {'id': 1, 'sender_id': 1, 'content': 'Hey Priya, your post about Dijkstra was super helpful!', 'sent_at': dt(hours_ago=5)},
            {'id': 2, 'sender_id': 4, 'content': 'Glad it helped! Let me know if you have questions.', 'sent_at': dt(hours_ago=4, minutes_ago=30)},
            {'id': 3, 'sender_id': 1, 'content': 'Thanks for the Dijkstra tip!', 'sent_at': dt(hours_ago=4)},
        ],
    },
]

# ──────────────────────────────────────────────
# RESOURCES
# ──────────────────────────────────────────────
RESOURCES = [
    {
        'id': 1,
        'owner': USERS[0],
        'course': COURSES[0],
        'title': 'Database Systems Textbook (Ramakrishnan)',
        'type': 'textbook',
        'description': 'Gently used. Has some highlights in chapters 1-5.',
        'available': True,
        'created_at': dt(days_ago=5),
    },
    {
        'id': 2,
        'owner': USERS[3],
        'course': COURSES[1],
        'title': 'CLRS Algorithms Textbook',
        'type': 'textbook',
        'description': 'Introduction to Algorithms, 4th edition. Perfect condition.',
        'available': True,
        'created_at': dt(days_ago=10),
    },
    {
        'id': 3,
        'owner': USERS[0],
        'course': COURSES[0],
        'title': 'CSCI 411 Lecture Notes - Full Semester',
        'type': 'notes',
        'description': 'Complete typed notes covering all lectures. Includes ER diagrams, SQL, and query optimization.',
        'available': True,
        'created_at': dt(days_ago=3),
    },
    {
        'id': 4,
        'owner': USERS[2],
        'course': COURSES[2],
        'title': 'MATH 221 Study Guide - Midterm 2',
        'type': 'notes',
        'description': 'Covers eigenvalues, eigenvectors, diagonalization. Very detailed.',
        'available': False,
        'created_at': dt(days_ago=7),
    },
]

# ──────────────────────────────────────────────
# EVENTS
# ──────────────────────────────────────────────
EVENTS = [
    {
        'id': 1,
        'title': 'Atwood After Dark',
        'type': 'Campus Event',
        'description': 'Annual campus night event at Atwood Hall. Food, music, and activities.',
        'date': 'Mar 15, 2026',
        'time': '8:00 PM',
        'location': 'Atwood Hall',
        'post_count': '2.3K',
        'rsvp_count': 340,
    },
    {
        'id': 2,
        'title': 'Huskies First Four',
        'type': 'Sports Event',
        'description': 'UW Huskies basketball NCAA tournament First Four game.',
        'date': 'Mar 18, 2026',
        'time': '6:00 PM',
        'location': 'Alaska Airlines Arena',
        'post_count': '5.1K',
        'rsvp_count': 1200,
    },
    {
        'id': 3,
        'title': 'Hackathon 2026',
        'type': 'Tech Event',
        'description': '24-hour hackathon hosted by UW CSE. Open to all majors. Prizes up to $5000.',
        'date': 'Mar 22, 2026',
        'time': '9:00 AM',
        'location': 'Paul G. Allen Center',
        'post_count': '8.7K',
        'rsvp_count': 520,
    },
]

# ──────────────────────────────────────────────
# FOLLOW SUGGESTIONS
# ──────────────────────────────────────────────
FOLLOW_SUGGESTIONS = [
    {**u, 'mutual_followers': ['Sara Malik']} for u in USERS if not u.get('is_following')
]
