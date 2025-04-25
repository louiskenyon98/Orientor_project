def vectorize_user_profiles(df, model_name="all-MiniLM-L6-v2"):
    from sentence_transformers import SentenceTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    import numpy as np
    # Text embedding
    text_fields = ['Story', 'Interests', 'Hobbies', 'Unique Quality', 'Learning Style',
                   'Favourite movie', 'Favourite Book', 'Role Model']
    df['text_input'] = df.apply(lambda row: " ".join(str(row[col]) for col in text_fields if pd.notnull(row[col])), axis=1)
    model = SentenceTransformer(model_name)
    text_vecs = model.encode(df['text_input'].tolist(), show_progress_bar=True)

    # Structured
    categorical = ['Sex', 'Major', 'Country', 'Learning Style']
    numeric = ['Age', 'GPA', 'Year']

    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    cat_vecs = ohe.fit_transform(df[categorical].fillna("missing"))

    scaler = StandardScaler()
    num_vecs = scaler.fit_transform(df[numeric].fillna(0))

    structured_vecs = np.hstack([cat_vecs, num_vecs])
    return np.hstack([text_vecs, structured_vecs])


