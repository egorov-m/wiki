import React from 'react';
import Button from '@mui/material/Button';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import AppBar from '@mui/material/AppBar';
import Typography from '@mui/material/Typography';
import {Box} from "@mui/system";
import PersonIcon from '@mui/icons-material/Person';
import "../Styles/BaseColors.css"
import "../Styles/Navbar.css"


export default function AppNavbar(props) {
    const [anchorEl, setAnchorEl] = React.useState(null);

    const handleMenuOpen = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    function getLeftPanel() {

        let base =
            <div>
                <Typography variant="h6"
                            component="a"
                            href="#"
                            id="typography-home">
                    ГЛАВНАЯ
                </Typography>
                <Typography variant="h6"
                            component="a"
                            href="https://d-element.ru/?ysclid=lolx8ntig9911662351"
                            id="typography-home">
                    ПЕРЕЙТИ НА САЙТ
                </Typography>
            </div>


        if (props.user !== null && props.user.wiki_api_client !== null) {
            return (
                <div className="base-button">
                    <Stack direction="row" alignItems="center" spacing={2}>
                        {base}
                        {props.user.wiki_api_client.responsibility === 'ADMIN' ? (
                            <Button id="typography-home" href="#admin">
                                ИНСТРУМЕНТЫ АДМИНА
                            </Button>
                        ) : null}
                        <Button id="typography-home" href="#workspace/select">
                            ПРОЕКТЫ
                        </Button>
                    </Stack>
                </div>
            )
        } else return base
    }

    function getRightPanel() {
        if (props.user === null) {
            return (
                <Stack direction="row" spacing={2} sx={{ justifyContent: 'flex-end', marginLeft: 'auto' }}>
                    <Button id="base-button" /*sx={{color: '#423e42', ':hover': {backgroundColor: '#506796'}, background: '#637cad',}} */
                            variant="contained" href="#login">
                        ВОЙТИ
                    </Button>
                    <Button id="accent-button"  /*sx={{background:'#b07285', color: '#423e42', ':hover': {backgroundColor: '#8a4a5d'}}}*/
                            variant="contained" href="#signup">
                        ЗАРЕГИСТРИРОВАТЬСЯ
                    </Button>
                </Stack>
            );
        } else {
            return (
                <Stack direction="row" sx={{ justifyContent: 'flex-end', marginLeft: 'auto' }}>
                    <Button
                        variant="contained"
                        onClick={handleMenuOpen}
                        id="accent-button"
                        sx={{background:'#103070', color: '#b4cbfa', ':hover': {backgroundColor: '#001847'}}}
                    >
                        <PersonIcon/>
                        {props.user.username}
                    </Button>
                    <Menu
                        anchorEl={anchorEl}
                        open={Boolean(anchorEl)}
                        onClose={handleMenuClose}
                        anchorOrigin={{
                            vertical: 'bottom',
                            horizontal: 'right',
                        }}
                        transformOrigin={{
                            vertical: 'top',
                            horizontal: 'right',
                        }}
                    >
                        <MenuItem  onClick={()=> {
                            handleMenuClose()
                            window.location.href = "#profile"
                        }}>
                            Profile
                        </MenuItem>
                        <MenuItem onClick={()=> {
                            handleMenuClose()
                            window.location.href = "#logout"
                        }}>
                            Logout
                        </MenuItem>
                    </Menu>
                </Stack>
            );
        }
    }

    return (
        <>
            <Box sx={{flexGrow: 1}}>
                <AppBar position="fixed">
                    <Toolbar id="main-background">
                        {getLeftPanel()}
                        {getRightPanel()}
                    </Toolbar>
                </AppBar>
            </Box>
        </>
    )
}
