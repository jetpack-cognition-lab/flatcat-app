import React, { useState, useEffect } from "react"
import './App.css'
import Header from './components/Header'
import Footer from './components/Footer'
import Button from './components/Button'
import Message from './components/Message'
import HelpMessage from './components/HelpMessage'
import InteractButton from './components/InteractButton'
import WifiForm from './components/WifiForm'
import OnOff from './components/OnOff'
import SVGseparator from './components/SVGseparator'
// import BurgerButton from './components/BurgerButton'
import Inputer from './components/Inputer'

import ReactSlider from "react-slider";

import moment from 'moment';



function App() {


  // ### STATES ###

  // nickname
  const [fcuiName, setFcuiName] = useState('my flatcat')

  // preferences
  const [showMenu, setShowMenu] = useState(true)

  // update notification
  const [updateAvail, setUpdateAvail] = useState('unknown') // available, unknown or updated
  const [updaterStatus, setUpdaterStatus] = useState('none') // none, checked, downloaded, installed

  // wifi
  const [networkName, setNetworkName] = useState('')
  const [networkSecret, setNetworkSecret] = useState('')
  const [networkStatus, setNetworkStatus] = useState('none') // none, connecting, failed, connected

  // buttons
  const [buttonsInteractive, setButtonsInteractive] = useState([
    {
      id: 0,
      name: 'update',
      label: 'check for update',
      show_message: false,
      color: 'green',
      message: fcuiName+' is up to date',
      help: 'Here you can download and install a newer version of the flatcat software. Normally a new version comes with additional features and improved functionality.'
    },
    {
      id: 1,
      name: 'wifi connect',
      label: 'connect',
      show_message: false,
      color: 'green',
      message: fcuiName+' is connected to the internet',
      help: 'In this section you can connect the flatcat to your wifi router. Just enter the name of the router and the required password.'
    }

  ])

  // versions
  const [currentTime, setCurrentTime] = useState(0)
  const [currentVersion, setCurrentVersion] = useState(0)
  const [updaterList, setUpdaterList] = useState([])
  const [updaterListSelected, setUpdaterListSelected] = useState('current')

  // on/off options
  const [fcuiOnOffs, setFcuiOnOffs] = useState([
    {
      id: 1,
      name: 'option eins',
      value: false,
      help: 'Lorem ipsum nemo laboriosam fuga aliquam nobis, ab, atque animi magni! Quaerat quis vero delectus repellat maxime.'
    },
    {
      id: 2,
      name: 'option 2',
      value: true,
      help: 'Lorem ipsum dolor sit amet, voluptatum aliquam Placeat.'
    }
  ])

  // preferences (on/off options)
  const [backendOptions, setBackendOptions] = useState([
    {
      id: 1,
      name: 'training wheels',
      value: true,
      help: 'Shows you descriptions and hints on all options, like this one.'
    },
    {
      id: 2,
      name: 'dark mode',
      value: false,
      help: 'A dark colored layout.'
    }
  ])

  console.log(`flatcat-app/App.js ${fcuiName}`)



  // ### FUNCTIONS ###

  const hideUpdate = () => {
    setUpdateAvail('postpone')
  }

  const toggleMenu = () => {
    setShowMenu(!showMenu)
  }

  // check if wifi is connected
  const messageCondWifi = () => {
    if (networkStatus === 'connected') {
      return true
    } else {
      return false
    }
  }

  // interactive button
  const showMessageButtonsInt = (index, message) => {
    let newArr = [...buttonsInteractive]
    newArr[index].message = message
    newArr[index].show_message = true
    setButtonsInteractive(newArr)
  }
  const setLabelButtonsInt = (index, label) => {
    let newArr = [...buttonsInteractive]
    newArr[index].message = ''
    newArr[index].label = label
    newArr[index].show_message = false
    setButtonsInteractive(newArr)
  }

  // backend options
  const toggleOptionBackend = index => e => {
    let newArr = [...backendOptions]
    newArr[index].value = !backendOptions[index].value
    setBackendOptions(newArr)
  }

  // on/off options
  const toggleOptionOnOffs = index => e => {
    let newArr = [...fcuiOnOffs]
    newArr[index].value = !fcuiOnOffs[index].value
    setFcuiOnOffs(newArr)
  }

  //
  const handleSubmitUpdaterList = (event) => {
    console.log(`handleSubmitUpdaterList pre ${updaterListSelected}`)
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(
        {
          title: 'React POST Request Example',
          install_version: updaterListSelected
        }
      )
    };
    fetch('/api/updater/download', requestOptions).then(res => res.json()).then(data => {
      // setCurrentTime(data.time)
      console.log(data.message)
    });
  }

  const handleChangeUpdaterList = (event) => {
    console.log(`handleChangeUpdaterList pre ${updaterListSelected}`)
    setUpdaterListSelected(event.target.value)
    console.log(`handleChangeUpdaterList post ${updaterListSelected}`)
  }

  const handleSubmitInstall = (event) => {
    showMessageButtonsInt(0, 'installing . . .')
    console.log(`handleSubmitInstall ${event}`)
    console.log(`handleSubmitInstall ${updaterListSelected}`)
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(
        {
          // title: 'React POST Request Example',
          run_hot: true,
          install_backup: false,
          install_version: updaterListSelected
        }
      )
    };
    fetch('/api/updater/install', requestOptions).then(res => res.json()).then(data => {
      // setCurrentTime(data.time);
      console.log(data.data.message)
    });
    setUpdaterStatus("installed")
    showMessageButtonsInt(0, 'installation successful, '+fcuiName+' is up to date')
  }

  // download button clicked
  const handleDownloadAndInstall = (e) => {
    if (networkStatus === 'connected') {
      showMessageButtonsInt(0, 'checking for update . . .')
      if (updaterStatus === "none") {
        let newestUpdate = updaterList.sort((a, b) => (a < b) ? 1 : -1)[0]
        setUpdaterListSelected(newestUpdate)
        if (newestUpdate === 'current') {
          showMessageButtonsInt(0, fcuiName+' is up to date')
        } else {
          setUpdaterStatus("checked")
          setLabelButtonsInt(0, "download & install")
        }
      } else if (updaterStatus === "checked") {
        setUpdaterStatus("downloaded")
        showMessageButtonsInt(0, 'downloading . . .')
        handleSubmitInstall()
      }
    } else {
      showMessageButtonsInt(0, "no internet connecting")
      setTimeout(() => {
       setLabelButtonsInt(0, "check for update")
      }, 5000);
    }
  }

  // wifi submit
  const handleWifiForm = (e) => {
    console.log('handleWifiForm')
    // TODO: wifi connection

    // error handling
    if (networkName && networkSecret) {
      showMessageButtonsInt(1, 'trying to connect . . .')
    } else {
      showMessageButtonsInt(1, 'please enter a network name and a password!')
      setTimeout(() => {
       setLabelButtonsInt(1, "connect")
      }, 5000)
    }
  }

  // get current time
  useEffect(() => {
    fetch('/api/time').then(res => res.json()).then(data => {
      console.log(`data.time ${data.time}`)
      console.log(`moment(data.time) ${moment.unix(data.time)}`)
      setCurrentTime(moment.unix(data.time).format('YYYY-MM-DD HH-mm-ss'));
      // setCurrentTime(data.time);
    });
  }, []);

  // get current version
  useEffect(() => {
    fetch('/api/updater/version').then(res => res.json()).then(data => {
      console.log(JSON.stringify(data, null, 4));
      console.log(`data.data.version ${data.data.version}`)
      setCurrentVersion(data.data.version);
    });
  }, []);

  // get list of updates
  useEffect(() => {
    fetch('/api/updater/list').then(res => res.json()).then(data => {
      console.log(`data ${data.data.message}`)
      setUpdaterList(data.data.list_of_updates);
    });
  }, []);


  // ### RETURN ###

  return (
    <div className="App">

    <div
      id="fc_wrap"
      className={`${backendOptions[0].value ? 'helping' : ''}
      ${showMenu ? 'withMenu' : ''}
      ${backendOptions[1].value ? 'darked' : ''}
      ${showMenu ? 'withMenu' : ''}`}
    >

    <Header
      name={fcuiName}
      toggleMenu={toggleMenu}
      showMenu={showMenu}
    />

    <Message
      theMessage='blub'
      condition={messageCondWifi}
    />

    <section>
    <h2>Version</h2>
    <p>flatcat time is {currentTime}.</p>
    <p>flatcat app version is {currentVersion}.</p>
    <SVGseparator a={60} b={20} c={70} d={40} width={8} />
    </section>

    <section>
    <div>
    <h2>Available Updates</h2>
    <select onChange={handleChangeUpdaterList}>
    {
      updaterList.sort((a, b) => (a < b) ? 1 : -1).map(
        team => <option key={team} value={team.replace(/flatcat-(.*).ar/, '$1')}>{team}</option>
      )
    }
    </select>
    <p><button onClick={handleSubmitUpdaterList}>download selected update</button></p>
    <p><button onClick={handleSubmitInstall}>install selected update</button></p>
    </div>
    <SVGseparator a={60} b={20} c={70} d={40} width={8} />
    </section>

    <section className={`${updateAvail === 'available' ? 'visible' : 'hidden'}`}>
    <h2>Update available</h2>
    <Button
      color='green'
      text='download & install'
      onClick={handleSubmitInstall}
      postpone={hideUpdate}
      abort
    />
    <SVGseparator a={60} b={20} c={70} d={40} width={8} />
    </section>

    <section className="fc_onoff">
    <h2>Option group</h2>
    {fcuiOnOffs.map((onOffOption, index) => (
      <OnOff
        key={onOffOption.id}
        onOffOption={onOffOption}
        onClick={toggleOptionOnOffs(index)}
      />
    ))}
    <SVGseparator a={60} b={20} c={70} d={40} width={8} />
    </section>

    <section className="fc_slider">
    <ReactSlider
    className="vertical-slider"
    thumbClassName="example-thumb"
    trackClassName="example-track"
    orientation="vertical"
    />
    <div className="clock_wrap">
    <div className="clock" id="clc_1">
    </div>
    </div>
    <SVGseparator a={20} b={60} c={20} d={20} width={8} />
    </section>

    {/* PREFERENCES */}
    <div className={`theMenu ${showMenu && "visible"}`}>

    <svg id="themenu_top" width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
    <polygon points="0,100 33,30 66,100 100,100 " />
    </svg>

    <section>
    <h2>Preferences</h2>
    </section>

    <HelpMessage helpMessage='Welcome to preferences! Here you can establish an internet connecting, change the name of your flatcat, update your software and so much more.' />

    <section>
    <h3>Update</h3>
    <InteractButton
      color={buttonsInteractive[0].color}
      label={buttonsInteractive[0].label}
      message={buttonsInteractive[0].message}
      show_message={buttonsInteractive[0].show_message}
      onClick={handleDownloadAndInstall}
    />
    <p className='help_message'>{buttonsInteractive[0].help}</p>
    <SVGseparator a={60} b={20} c={70} d={40} width={12} />
    </section>

    <section>
    <h3>Wifi</h3>
    <WifiForm
      networkName={networkName}
      setNetworkName={setNetworkName}
      networkSecret={networkSecret}
      setNetworkSecret={setNetworkSecret}
      handleWifiForm={handleWifiForm}
      fcuiName={fcuiName}
      buttonsInteractive={buttonsInteractive}
    />
    <p className='help_message'>{buttonsInteractive[1].help}</p>
    <SVGseparator a={60} b={20} c={70} d={40} width={12} />
    </section>

    <section>
    <h3>Name</h3>
    <Inputer
      setFcuiName={setFcuiName}
      Value={fcuiName}
    />
    <SVGseparator a={20} b={60} c={20} d={20} width={12} />
    </section>

    <section className="fc_onoff">
    <h3>Layout</h3>
    {backendOptions.map((backendOption, index) => (
      <OnOff
        key={backendOption.id}
        onOffOption={backendOption}
        onClick={toggleOptionBackend(index)}
      />
    ))}
    <SVGseparator a={50} b={60} c={50} d={10} width={12} />
    </section>

    <section className={`notice ${updateAvail === 'updated' ? 'visible' : 'hidden'}`}>
    <h3>Update</h3>
    <p>Your flatcat is up to date.</p>
    <SVGseparator a={60} b={20} c={70} d={40} width={12} />
    </section>

    <section>
    <div style={{height: 250+'px'}}></div>
    </section>

    <button className="fc_btn_option closer" onClick={toggleMenu}>&times;</button>

    </div>

    <Footer />

    </div>

    </div>
  );
}

export default App;
