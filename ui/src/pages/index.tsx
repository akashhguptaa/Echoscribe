import Navbar from '../components/Navbar'
import HeroSection from '../components/HeroSection'
import { useState } from 'react'

export default function Home(){
   const [start, setStart] = useState<boolean>(false)
   const resetStart = ()=>{
    setStart(false)
   }
  return(
    <div className='bg-gradient-to-r from-[#E0F5F8] to-transparent '>

    <Navbar resetStart={resetStart}/>
    <HeroSection  start={start} setStart={setStart}/>
    </div>
  )
}