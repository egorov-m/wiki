import {Typography} from "@mui/material";
import React from "react";


export default function TextBlock({block}){

    return(
        <Typography dangerouslySetInnerHTML={{ __html: block.content}} />
    )
}