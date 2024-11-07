# Disxtractor
shitty script to get all the images and media from a discord server

# Usage
- install all the stuff with pip ```pip install -r requirements.txt```

- create a ```.env``` file and put your token then execute the script with ```python main.py``` [how to get your token](https://stackoverflow.com/questions/67348339/any-way-to-get-my-discord-token-from-browser-dev-console)
- choice the fucking server do you want to scrap 
- enjoy 

## Config

```json
{
    "save_guild_by": "name",
    "save_user_by": "name",
    "include": {
        "video": true,
        "image": true,
        "nsfw": true
    }
}
```

### Configuration Options

| Key             | Description                                      | Possible Values |
|-----------------|--------------------------------------------------|-----------------|
| save_guild_by   | Method to save guild information                 | `name`, `id`    |
| save_user_by    | Method to save user information                  | `name`, `id`    |
| include.video   | Whether to include videos in the extraction      | `true`, `false` |
| include.image   | Whether to include images in the extraction      | `true`, `false` |
| include.nsfw    | Whether to include NSFW content in the extraction| `true`, `false` |
