MAPPINGS = dict()
MAPPINGS["PROVIDER"] = {
        # mapping
        "provider": {
            "properties": {
                "menus": {
                    "type": "nested",
                    "properties": {
                        "menu_items": {
                            "type": "nested",
                            "properties": {
                                "name": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                },
                "location": {
                    "type": "geo_point"
                }
            }
        }
    }
