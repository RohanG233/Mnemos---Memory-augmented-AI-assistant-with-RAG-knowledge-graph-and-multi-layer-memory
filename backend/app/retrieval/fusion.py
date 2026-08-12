from collections import defaultdict

from app.core.config import RRF_K


def reciprocal_rank_fusion(
    rankings,
    k=RRF_K
):
    """
    Combine multiple ranked lists using
    Reciprocal Rank Fusion.

    Parameters
    ----------
    rankings : list[list[int]]
        Ranked document IDs from different retrievers.

    k : int
        RRF constant.

    Returns
    -------
    list[tuple]
        Document IDs with their fused scores.
    """

    scores = defaultdict(float)

    for ranking in rankings:

        for rank, doc_id in enumerate(
            ranking,
            start=1
        ):

            scores[doc_id] += 1 / (
                k + rank
            )

    return sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )