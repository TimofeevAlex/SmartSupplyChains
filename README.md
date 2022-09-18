# Smart Supply Chains

Our web app is aimed to assist supply chain managers in their daily work. This includes not only identifying potential risks of delays during goods delivering but also finding the workarounds for such issues to guarantee shelves being full of products loved by the Migros customers. Wide variety of data sources including news, social media and weather services are fused to get the final conclusion about the time security of the route. You can see most severe ones drawn on the world map along with the routes typically used for delivering goods for Swiss citizens.

Please, feel free to play with our [demo](https://mydashboard-cauzu3pgqa-ew.a.run.app/) and try to solve some supply chain problems happening right now in the world!

## Prerequisites
- Create a [Google Cloud project](https://cloud.google.com/docs/get-started)
- Create a [Firestore in Native Mode](https://cloud.google.com/firestore/docs/create-database-server-client-library#create_a_in_native_mode_database)

## Deploy
Run following code on Cloud Shell, or anywhere Google Cloud SDK installed.

```
$ gcloud run deploy mydashboard --source . --timeout=3600
```

## Ingesting dummy mobility data
Run following python script on Cloud Shell, or anywhere Google Cloud SDK installed.

```
$ python3 ingest.py
```

## Debug on local
If you are using [Cloud Shell Editor](ide.cloud.google.com) or VS Code, click `"Cloud Code"` then select `"Run on Cloud Run Emulator"`.

You can also run the script directly. 
```
$ streamlit run app.py --server.enableCORS=false
```

