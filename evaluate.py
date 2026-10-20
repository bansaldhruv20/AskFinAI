import json
from faq_engine import FAQEngine, ROOT


def main():
    engine = FAQEngine()

    cases = json.loads(
        (ROOT / "evaluation/cases.json").read_text()
    )

    results = []

    for case in cases:
        result = engine.search(case["query"])

        actual = (
            result["question"]
            if result["accepted"]
            else None
        )

        results.append(
            {
                **case,
                "actual_question": actual,
                "score": result["score"],
                "passed": (
                    actual == case["expected_question"]
                ),
            }
        )

    report = {
        "description": (
            "Authored demo regression set; "
            "not production accuracy or ticket deflection."
        ),
        "threshold": engine.threshold,
        "passed": sum(
            result["passed"] for result in results
        ),
        "total": len(results),
        "results": results,
    }

    output = json.dumps(report, indent=2)

    (ROOT / "evaluation/results.json").write_text(
        output + "\n"
    )

    print(output)

    return (
        0
        if all(result["passed"] for result in results)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
