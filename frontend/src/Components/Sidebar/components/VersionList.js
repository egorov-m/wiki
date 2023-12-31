import {api} from "../../../Config/app.config";
import React, {useEffect, useState} from "react";
import {Version} from "./Version";
import {Divider, List} from "@mui/material";
import Preload from "../../Preload";




export const VersionList = ({wikiObject, show, onRollback, onMouseLeave, isBlock, listStyles}) => {


    const [versions, setVersions] = useState([]);
    const [versionsLoad, setVersionsLoad] = useState(true);

    const fetchVersions = async () =>{
        try {
            setVersions([])
            let res;
            if (isBlock) {
                res = await api.getBlockVersions(wikiObject.id)
            } else {
                res = await api.getDocVersions(wikiObject.id)
            }

            setVersions(res);
            setVersionsLoad(false);
        }
        catch (e){
            console.log(e)
        }
    }

    const handleRollback = async (object_id, commit_id) => {
        onRollback(object_id, commit_id)
    }
    
    useEffect(() => {
        fetchVersions()

    }, [])

    if (show)
        return(
            <List style={listStyles} onMouseLeave={onMouseLeave}>
                {versionsLoad? <Preload/> : versions.map((item) => {
                    return (
                        <>
                            <Version version={item} onRollback={handleRollback}/>
                            <Divider variant="inset" component="li" />
                        </>
                    )
                })}
            </List>
        )
    else
        return null
}