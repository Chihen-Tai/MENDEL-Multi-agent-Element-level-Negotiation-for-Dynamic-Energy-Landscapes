from mendel.parser import parse_reaction_smiles
from mendel.identifier import identify_functional_groups, get_group_summary
from mendel.predictor import predict_roles_for_reaction, summarize_predictions
from mendel.types import ReactionContext


TEST_CASES = [
    {
        "name": "Aldol-like: acetone + methyl bromide",
        "smiles": "CC(=O)C.CBr>>CC(=O)CO",
        "context": ReactionContext.ionic,
    },
    {
        "name": "SN2: methyl bromide + hydroxide",
        "smiles": "CBr.[OH-]>>CO.[Br-]",
        "context": ReactionContext.ionic,
    },
    {
        "name": "Carbonyl electrophile: acetone",
        "smiles": "CC(=O)C>>CC(=O)C",
        "context": ReactionContext.ionic,
    },
    {
        "name": "Ester electrophile: methyl acetate",
        "smiles": "CC(=O)OC>>CC(=O)OC",
        "context": ReactionContext.ionic,
    },
    {
        "name": "Diels-Alder simple",
        "smiles": "C=CC=C.C=C>>C1CCC=CC1",
        "context": ReactionContext.pericyclic,
    },
    {
        "name": "Benzylic radical site: toluene",
        "smiles": "Cc1ccccc1>>Cc1ccccc1",
        "context": ReactionContext.radical,
    },
    {
        "name": "Phenol acidity / weak nucleophile",
        "smiles": "c1ccccc1O>>c1ccccc1O",
        "context": ReactionContext.ionic,
    },
    {
        "name": "Nitro group",
        "smiles": "C[N+](=O)[O-]>>C[N+](=O)[O-]",
        "context": ReactionContext.ionic,
    },
    {
        "name": "Nitrile electrophile",
        "smiles": "CC#N>>CC#N",
        "context": ReactionContext.ionic,
    },
    {
        "name": "Alcohol control",
        "smiles": "CCO>>CCO",
        "context": ReactionContext.ionic,
    },
]


def run_case(case):
    print("\n" + "=" * 80)
    print(case["name"])
    print(case["smiles"])
    print("Context:", case["context"].value)

    rxn = parse_reaction_smiles(case["smiles"], context=case["context"])
    groups = identify_functional_groups(rxn)
    report = predict_roles_for_reaction(rxn, groups)

    group_summary = get_group_summary(groups)
    prediction_summary = summarize_predictions(report.predictions)

    print("\nGroup summary:")
    print(group_summary)

    print("\nPredictions:")
    for pred in report.predictions:
        print(
            pred.group_id,
            pred.group_type.value,
            "=>",
            pred.predicted_role.value,
            pred.confidence,
            "|",
            pred.reason,
        )

    print("\nPrediction summary:")
    print(prediction_summary)

    assert len(groups) == len(report.predictions), (
        "Each group must receive one prediction."
    )

    for pred in report.predictions:
        assert pred.predicted_role is not None
        assert 0.0 <= pred.confidence <= 1.0
        assert pred.reason is not None and len(pred.reason) > 0


if __name__ == "__main__":
    for case in TEST_CASES:
        run_case(case)

    print("\n" + "=" * 80)
    print("Manual Phase 5 check finished.")
    print("If pytest also passes, Phase 5 is good enough to move to Phase 6.")
