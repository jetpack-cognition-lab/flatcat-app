const BurgerButton = ({ click, close }) => {
  if (close) {
    return <button className="fc_btn_option closer" onClick={click}>&times;</button>
  } else {
    return <button className="fc_btn_option" onClick={click}>&#9776;</button>
  }

}

export default BurgerButton
