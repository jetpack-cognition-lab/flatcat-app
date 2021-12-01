import React, { useState, useEffect } from "react"
import './App.css'
import Header from './components/Header'
import Button from './components/Button'
import OnOff from './components/OnOff'
import SVGseparator from './components/SVGseparator'
// import BurgerButton from './components/BurgerButton'
import Inputer from './components/Inputer'

import ReactSlider from "react-slider";

import moment from 'moment';



function App() {

  // STATES

  const [fcuiName, setFcuiName] = useState('my flatcat')

  const [showMenu, setShowMenu] = useState(false);

  const [updateAvail, setUpdateAvail] = useState('available');
  // available, unknown, updated

  // const [trainingWheels, setTrainingWheels] = useState(true)

  const [currentTime, setCurrentTime] = useState(0);
  const [currentVersion, setCurrentVersion] = useState(0);
  const [updaterList, setUpdaterList] = useState([]);
  const [updaterListSelected, setUpdaterListSelected] = useState('current');

  const [confFlatcat, setConfFlatcat] = useState({});

  const [confWifiApState, setConfWifiApState] = useState(true);
  const [confWifiWlanSsid, setConfWifiWlanSsid] = useState('None');

  // const [elements, setElements] = useState(null);
  // setElements(formJSON[0])
  // const {fields,page_label} = elements??{};

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

  const [backendOptions, setBackendOptions] = useState([
    {
      id: 1,
      name: 'training wheels',
      value: true,
      help: 'Shows you descriptions and hints on all options.'
    },
    {
      id: 2,
      name: 'dark mode',
      value: false,
      help: 'A dark colored layout.'
    }

  ])

  console.log(`flatcat-app/App.js ${fcuiName}`)
  
  // FUNCTIONS

  const hideUpdate = () => {
    setUpdateAvail('postpone')
  }

  const toggleMenu = () => {
    setShowMenu(!showMenu);
  }

  const toggleOptionBackend = index => e => {
    let newArr = [...backendOptions]
    newArr[index].value = !backendOptions[index].value
    setBackendOptions(newArr)
  }

  const toggleOptionOnOffs = index => e => {
    let newArr = [...fcuiOnOffs]
    newArr[index].value = !fcuiOnOffs[index].value
    setFcuiOnOffs(newArr)
  }

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
      // setCurrentTime(data.time);
      console.log(data.message)
    });
  }

  const handleChangeUpdaterList = (event) => {
    console.log(`handleChangeUpdaterList pre ${updaterListSelected}`)
    setUpdaterListSelected(event.target.value)
    console.log(`handleChangeUpdaterList post ${updaterListSelected}`)
  }

  const handleSubmitInstall = (event) => {
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

  // get configuration dictionary
  useEffect(() => {
    fetch('/api/configuration').then(res => res.json()).then(data => {
      console.log(`configuration ${data.data}`)
      setConfFlatcat(data.data);
    });
  }, []);


  // RETURN

  return (
    <div className="App">
      
      <div id="fc_wrap" className={`${backendOptions[0].value ? 'helping' : ''} ${showMenu ? 'withMenu' : ''} ${backendOptions[1].value ? 'darked' : ''} ${showMenu ? 'withMenu' : ''}`}>

      <Header name={fcuiName} toggleMenu={toggleMenu} showMenu={showMenu} />

      <section>
      <p>flatcat time is {currentTime}.</p>

      <p>flatcat app version is {currentVersion}.</p>
      
      <SVGseparator a={60} b={20} c={70} d={40} width={8} />
      </section>
      
      <section>
      <div>
      <p>Available updates</p>
      <select onChange={handleChangeUpdaterList}>
      {
	updaterList.sort((a, b) => (a < b) ? 1 : -1).map(
	  team => <option key={team} value={team.replace(/flatcat-(.*).ar/, '$1')}>{team}</option>)
      }
      </select>
      <p><button onClick={handleSubmitUpdaterList}>download selected update</button></p>
      <p><button onClick={handleSubmitInstall}>install selected update</button></p>
      </div>
      <SVGseparator a={60} b={20} c={70} d={40} width={8} />
      </section>


      <section>
      <p>Configure Wifi</p>

      <p>Access point: {confWifiApState ? ('blub') : ('bla') }</p>

      <p>WLAN: {confWifiWlanSsid}</p>
      <label>SSID
      <input type="text" value={confWifiWlanSsid} onChange={setConfWifiWlanSsid} />
      </label>

      {
	// Object.entries(confFlatcat).map(([key, val]) => <div>{key} : {val} </div>)
      }

      <div><pre>{JSON.stringify(confFlatcat, null, 2) }</pre></div>
      <SVGseparator a={60} b={20} c={70} d={40} width={8} />
      </section>
      
      <section className={`${updateAvail === 'available' ? 'visible' : 'hidden'}`}>
      <h2>Update available</h2>
      <Button color='green' text='download & install' onClick={handleSubmitInstall} postpone={hideUpdate} abort />
      <SVGseparator a={60} b={20} c={70} d={40} width={8} />
      </section>

        <section className="fc_onoff">
        <h2>Option group</h2>

          {fcuiOnOffs.map((onOffOption, index) => (
            <OnOff key={onOffOption.id} onOffOption={onOffOption} onClick={toggleOptionOnOffs(index)} />
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




      <div className={`theMenu ${showMenu ? "visible" : ""}`}>

        <svg id="themenu_top" width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
          <polygon points="0,100 33,30 66,100 100,100 " />
        </svg>

        <section>
        <h2>Preferences</h2>
        </section>

        <section className={`${updateAvail !== 'updated' && updateAvail !== 'unknown' ? 'visible' : 'hidden'}`}>
          <h3>Update available</h3>
          <Button color='green' text='download & install' />
          <SVGseparator a={60} b={20} c={20} d={60} width={12} />
        </section>

        <section className={`notice ${updateAvail === 'unknown' ? 'visible' : 'hidden'}`}>
          <h3>Update</h3>
          <p>Please connect to the internet to check for updates!</p>
          <Button text='check for updates' />
          <SVGseparator a={60} b={20} c={20} d={60} width={12} />
        </section>



        <section>
          <h3>Name</h3>
          <Inputer setFcuiName={setFcuiName} Value={fcuiName} />
          <SVGseparator a={20} b={60} c={20} d={20} width={12} />
        </section>

        <section className="fc_onoff">
        <h3>Layout</h3>
          {backendOptions.map((backendOption, index) => (
            <OnOff key={backendOption.id} onOffOption={backendOption} onClick={toggleOptionBackend(index)} />
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

  </div>

  </div>
  );
}

export default App;
