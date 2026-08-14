CORE_DSA_AREAS = {
    "Arrays": {
        "array",
        "arrays",
    },

    "Hash Table": {
        "hash table",
        "hash map",
        "hashmap",
    },

    "Strings": {
        "string",
        "strings",
    },

    "Linked List": {
        "linked list",
        "linked lists",
    },

    "Stack": {
        "stack",
        "stacks",
    },

    "Queue": {
        "queue",
        "queues",
    },

    "Binary Search": {
        "binary search",
    },

    "Sorting": {
        "sorting",
        "sort",
    },

    "Two Pointers": {
        "two pointers",
    },

    "Sliding Window": {
        "sliding window",
    },

    "Trees": {
        "tree",
        "trees",
        "binary tree",
        "binary search tree",
        "avl tree",
    },

    "Graphs": {
        "graph",
        "graphs",
        "depth-first search",
        "breadth-first search",
        "union find",
        "topological sort",
    },

    "Heap / Priority Queue": {
        "heap",
        "heaps",
        "priority queue",
        "priority queues",
    },

    "Greedy": {
        "greedy",
    },

    "Dynamic Programming": {
        "dynamic programming",
        "dp",
    },
}


def normalize_tag(tag: str) -> str:

    return " ".join(
        tag.strip().lower().split()
    )


def classify_skill(
    problems_solved: int,
) -> str:

    if problems_solved <= 0:
        return "no_evidence"

    if problems_solved < 5:
        return "limited"

    if problems_solved < 15:
        return "developing"

    return "strong"


def build_normalized_skill_counts(
    skill_counts: dict[str, int],
) -> dict[str, int]:

    normalized = {}

    for tag, count in skill_counts.items():

        if not tag:
            continue

        normalized_tag = normalize_tag(tag)

        if not normalized_tag:
            continue

        normalized[normalized_tag] = (
            normalized.get(
                normalized_tag,
                0,
            )
            + max(count, 0)
        )

    return normalized


def build_core_dsa_coverage(
    skill_counts: dict[str, int],
) -> dict[str, dict]:

    normalized_counts = (
        build_normalized_skill_counts(
            skill_counts
        )
    )

    coverage = {}

    for area, tags in CORE_DSA_AREAS.items():

        matching_counts = [
            normalized_counts.get(
                normalize_tag(tag),
                0,
            )
            for tag in tags
        ]

        # IMPORTANT:
        #
        # LeetCode tags overlap.
        #
        # Example:
        # Tree = 24
        # Binary Tree = 24
        #
        # These should NOT become 48.
        #
        # We use the strongest relevant evidence
        # rather than blindly summing overlapping tags.

        count = max(
            matching_counts,
            default=0,
        )

        coverage[area] = {
            "problems_solved": count,
            "evidence": classify_skill(
                count
            ),
        }

    return coverage