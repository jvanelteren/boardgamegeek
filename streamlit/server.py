from fastai import *
from fastai.vision import *
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import urllib 

export_file_url = 'https://drive.google.com/uc?export=download&id=1G1e24nRTqMog5-d3CuRTfJ2yzhAO49xT'
export_file_name = 'export-3cycles1e-2-bs100000factors50yrange2-10wd005'



path = Path(__file__).parent

async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

async def setup_learner():
    await download_file(export_file_url, path/export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise

async def setup_gamelist():

    games = pd.read_csv('app/models/games_by_all_users.csv',index_col='primary')
    games.sort_values('usersrated',ascending=False, inplace=True)
    games.reset_index(inplace=True)
    return games

loop = asyncio.get_event_loop()
# tasks = [asyncio.ensure_future(setup_learner())]
tasks = [asyncio.ensure_future(setup_gamelist()),asyncio.ensure_future(setup_learner())]
games_by_all_users = loop.run_until_complete(asyncio.gather(*tasks))[0]
learner = loop.run_until_complete(asyncio.gather(*tasks))[1]
print('path',path)
loop.close()



def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open().read())

async def analyze(request):
    data = await request.form()
    print('received data from web',data)
    selected_game = urllib.parse.unquote_plus(data['selected_game'])
    num_reviews = int(data['num_reviews'])
    num_similar_games = int(data['num_similar_games'])

    potential_games = games_by_all_users[games_by_all_users['usersrated']>=num_reviews]
    # TODO make sure games with small amount of reviews are still taken along
    if (games_by_all_users[games_by_all_users['primary']==selected_game]['usersrated'] < num_reviews).all():
        potential_games = potential_games.append([games_by_all_users[games_by_all_users['primary']==selected_game]],ignore_index=False)
    potential_games.reset_index(inplace=True)
    npweights = learner.weight(potential_games['primary'], is_item=True).numpy()
    game_bias = learner.bias(potential_games['primary'], is_item=True).numpy()
    potential_games['model_score']=game_bias
    potential_games['model_score']=potential_games['model_score'].astype('float64')
    potential_games['weights_sum']=np.sum(np.abs(npweights),axis=1)

    nn = NearestNeighbors(n_neighbors=num_similar_games)
    fitnn = nn.fit(npweights)

    res = potential_games[potential_games['primary']==(selected_game)]

    distances,indices = fitnn.kneighbors([npweights[res.index[0]]])
    distances
    result = potential_games.iloc[indices[0][:500]].copy()
    result['distance']=distances[0]

    #result['model_score'] = pd.to_numeric(result['model_score'])
    result = result.round(2)
    result = result[['thumbnail','primary','usersrated','bayesaverage','average','model_score','distance','id']].copy()
    result = result.to_numpy()


    return JSONResponse({'result': result.tolist()})
    # img_bytes = await (data['file'].read())
    # img = open_image(BytesIO(img_bytes))
    # prediction = learn.predict(img)[0]
    # return JSONResponse({'result': str(prediction)})

async def gamelist(request):
    data = await request.form()
    print(data)
    return JSONResponse({'result': games_by_all_users.to_numpy()[:,0].tolist()})
if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042)
    print('running')

