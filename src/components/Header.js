import BurgerButton from './BurgerButton'

const Header = ({ name, toggleMenu, showMenu }) => {
  return (
    <header className='fc_header'>
    <div className='header_svg' id='svg1'>
      <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
        <polygon points="0,100 28,30 70,0 100,14 100,0 0,0" />

      </svg>
    </div>

    <h1>{name}</h1>
    <div className='header_svg' id='fc_triangle'>
    <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polygon points="0,100 28,30 70,100 100,100" />
    </svg>
</div>
    <button className={`fc_btn_option ${showMenu ? 'hidden' : ''}`} onClick={toggleMenu}>&#9776;</button>
    </header>
  )
}

export default Header
